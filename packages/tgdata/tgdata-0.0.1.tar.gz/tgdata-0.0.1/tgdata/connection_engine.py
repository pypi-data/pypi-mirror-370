"""
Connection management engine for Telegram.
Handles connection pooling, rate limiting, retries, and health checks.
"""

import asyncio
import configparser
import logging
import time
from typing import Optional, List, Dict, Any, Union
from telethon import TelegramClient
from telethon.errors import FloodWaitError, AuthKeyUnregisteredError
from telethon.sessions import StringSession

from .models import ConnectionConfig, RateLimitInfo

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Manage multiple connections with rate limiting"""
    
    def __init__(self, max_connections: int = 3):
        self.max_connections = max_connections
        self.connections: List[TelegramClient] = []
        self.current_index = 0
        self.rate_limits: Dict[int, RateLimitInfo] = {}
        
    async def get_connection(self) -> TelegramClient:
        """Get next available connection using round-robin"""
        if not self.connections:
            raise ValueError("No connections in pool")
            
        # Try to find a connection not rate-limited
        attempts = 0
        while attempts < len(self.connections):
            conn = self.connections[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.connections)
            
            rate_info = self.rate_limits.get(id(conn), RateLimitInfo())
            if time.time() < rate_info.flood_wait_until:
                attempts += 1
                continue
                
            return conn
            
        # All connections rate-limited, return the one with shortest wait
        return min(self.connections, 
                  key=lambda c: self.rate_limits.get(id(c), RateLimitInfo()).flood_wait_until)
        
    def mark_rate_limited(self, conn: TelegramClient, wait_seconds: float):
        """Mark a connection as rate-limited"""
        rate_info = self.rate_limits.get(id(conn), RateLimitInfo())
        rate_info.flood_wait_until = time.time() + wait_seconds
        self.rate_limits[id(conn)] = rate_info
        logger.warning(f"Connection {id(conn)} rate-limited for {wait_seconds}s")
    
    def add_connection(self, conn: TelegramClient):
        """Add a connection to the pool"""
        self.connections.append(conn)
        
    async def close_all(self):
        """Close all connections in the pool"""
        for conn in self.connections:
            await conn.disconnect()
        self.connections.clear()


class ConnectionEngine:
    """
    Manages Telegram connections with advanced features.
    """
    
    def __init__(self, 
                 config_path: str = "config.ini",
                 pool_size: int = 1,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 exponential_backoff: bool = True):
        """
        Initialize connection engine.
        
        Args:
            config_path: Path to configuration file
            pool_size: Number of connections in pool (1 = no pooling)
            max_retries: Maximum retry attempts
            retry_delay: Initial retry delay in seconds
            exponential_backoff: Whether to use exponential backoff
        """
        self.config_path = config_path
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        
        self._config: Optional[ConnectionConfig] = None
        self._primary_client: Optional[TelegramClient] = None
        self._pool: Optional[ConnectionPool] = None
        self._health_check_interval = 300  # 5 minutes
        self._last_health_check = 0
        
    def _load_config(self) -> ConnectionConfig:
        """Load configuration from file"""
        if self._config:
            return self._config
            
        config = configparser.ConfigParser()
        config.read(self.config_path)
        
        # Handle case-insensitive section names
        telegram_section = None
        for section in config.sections():
            if section.lower() == 'telegram':
                telegram_section = section
                break
        
        if telegram_section is None:
            raise ValueError("No [telegram] or [Telegram] section found in config file")
        
        self._config = ConnectionConfig(
            api_id=config[telegram_section]['api_id'],
            api_hash=config[telegram_section]['api_hash'],
            session_file=config[telegram_section].get('session_file', 'telegram_session'),
            phone=config[telegram_section].get('phone'),
            username=config[telegram_section].get('username'),
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            exponential_backoff=self.exponential_backoff
        )
        
        return self._config
        
    async def get_client(self) -> TelegramClient:
        """
        Get a connected Telegram client.
        Uses pooling if enabled, otherwise returns primary client.
        """
        # Check if health check needed
        current_time = time.time()
        if current_time - self._last_health_check > self._health_check_interval:
            await self.health_check()
            self._last_health_check = current_time
            
        # Use pool if enabled
        if self.pool_size > 1 and self._pool:
            return await self._pool.get_connection()
            
        # Otherwise ensure primary client is connected
        if not self._primary_client:
            await self._init_primary_client()
            
        if not self._primary_client.is_connected():
            await self._connect_with_retry(self._primary_client)
            
        return self._primary_client
        
    async def _init_primary_client(self):
        """Initialize the primary client"""
        config = self._load_config()
        
        # Use username as session name for compatibility with original code
        session_name = config.username if config.username else config.session_file
        self._primary_client = TelegramClient(
            session_name,
            config.api_id,
            config.api_hash
        )
        
        await self._connect_with_retry(self._primary_client)
        
        # Initialize pool if needed
        if self.pool_size > 1:
            await self._init_pool()
            
    async def _init_pool(self):
        """Initialize connection pool"""
        config = self._load_config()
        self._pool = ConnectionPool(self.pool_size)
        
        # Add primary client to pool
        if self._primary_client:
            self._pool.add_connection(self._primary_client)
            
        # Create additional connections
        for i in range(1, self.pool_size):
            session_file = f"{config.session_file}_{i}"
            client = TelegramClient(
                session_file,
                config.api_id,
                config.api_hash
            )
            
            await self._connect_with_retry(client)
            self._pool.add_connection(client)
            
        logger.info(f"Initialized connection pool with {self.pool_size} connections")
        
    async def _connect_with_retry(self, client: TelegramClient):
        """Connect a client with retry logic"""
        config = self._load_config()
        
        try:
            # Use start() directly - it handles everything including retries
            await client.start(phone=config.phone)
            logger.info("Successfully connected and authenticated!")
            
        except FloodWaitError as e:
            wait_time = e.seconds
            logger.warning(f"Rate limited, waiting {wait_time} seconds...")
            
            if self._pool:
                self._pool.mark_rate_limited(client, wait_time)
                
            await asyncio.sleep(wait_time)
            # Retry after rate limit
            await client.start(phone=config.phone)
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Failed to connect: {e}")
                    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all connections.
        
        Returns:
            Dictionary with health status
        """
        logger.info("Performing connection health check...")
        
        status = {
            'timestamp': time.time(),
            'primary_connection': False,
            'pool_connections': [],
            'errors': []
        }
        
        try:
            # Check primary connection
            if self._primary_client:
                try:
                    if self._primary_client.is_connected():
                        await self._primary_client.get_me()
                        status['primary_connection'] = True
                        logger.info("Primary connection healthy")
                except Exception as e:
                    status['errors'].append(f"Primary connection error: {e}")
                    logger.warning(f"Primary connection unhealthy: {e}")
                    
            # Check pool connections
            if self._pool:
                for i, conn in enumerate(self._pool.connections):
                    try:
                        if conn.is_connected():
                            await conn.get_me()
                            status['pool_connections'].append({
                                'index': i,
                                'healthy': True,
                                'rate_limited': time.time() < self._pool.rate_limits.get(
                                    id(conn), RateLimitInfo()
                                ).flood_wait_until
                            })
                        else:
                            status['pool_connections'].append({
                                'index': i,
                                'healthy': False
                            })
                    except Exception as e:
                        status['errors'].append(f"Pool connection {i} error: {e}")
                        status['pool_connections'].append({
                            'index': i,
                            'healthy': False,
                            'error': str(e)
                        })
                        
        except Exception as e:
            status['errors'].append(f"Health check error: {e}")
            logger.error(f"Health check failed: {e}")
            
        return status
        
    async def validate_connection(self) -> bool:
        """
        Validate that we have a working connection.
        
        Returns:
            True if connection is valid
        """
        try:
            client = await self.get_client()
            await client.get_me()
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False
            
    async def handle_rate_limit(self, error: FloodWaitError, client: Optional[TelegramClient] = None, strategy: str = 'wait'):
        """
        Handle rate limit errors with configurable strategy.
        
        Args:
            error: The FloodWaitError from Telegram
            client: The client that hit the rate limit
            strategy: 'wait' (wait exact time) or 'exponential' (exponential backoff)
        """
        base_wait_time = error.seconds
        
        if strategy == 'exponential':
            # Add random jitter (0-30% extra) to prevent thundering herd
            import random
            jitter = random.uniform(0, 0.3)
            wait_time = base_wait_time * (1 + jitter)
            logger.warning(f"Rate limit hit! Using exponential backoff: waiting {wait_time:.1f}s (base: {base_wait_time}s)")
        else:
            wait_time = base_wait_time
            logger.warning(f"Rate limit hit! Waiting {wait_time} seconds...")
        
        if self._pool and client:
            self._pool.mark_rate_limited(client, wait_time)
            
        await asyncio.sleep(wait_time)
        
    async def close(self):
        """Close all connections"""
        if self._pool:
            await self._pool.close_all()
        elif self._primary_client:
            await self._primary_client.disconnect()
            
        self._primary_client = None
        self._pool = None
        logger.info("All connections closed")