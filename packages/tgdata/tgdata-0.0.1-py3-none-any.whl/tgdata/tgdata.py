"""
Unified Telegram Group Message Crawler.
Single class with all features, delegating to specialized engines.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union, Callable
import pandas as pd

from .connection_engine import ConnectionEngine
from .message_engine import MessageEngine
from .models import GroupInfo
from .utils import (
    format_message_for_display,
    export_to_json,
    export_to_csv,
    filter_messages_by_sender,
    filter_messages_by_content,
    get_message_statistics,
    save_profile_photos,
    create_metrics_report
)

logger = logging.getLogger(__name__)

class TgData:
    """
    Unified interface for Telegram group operations.
    All features in one place, with clean delegation to specialized engines.
    """
    
    def __init__(self,
                 config_path: str = "config.ini",
                 connection_pool_size: int = 1,
                 log_file: Optional[str] = None):
        """
        Initialize Telegram group handler.
        
        Args:
            config_path: Path to configuration file
            connection_pool_size: Number of connections (1 = no pooling)
            log_file: Optional log file path
        """
        # Set up logging
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
            
        # Initialize engines
        self.connection_engine = ConnectionEngine(
            config_path=config_path,
            pool_size=connection_pool_size
        )
        
        self.message_engine = MessageEngine(
            connection_engine=self.connection_engine
        )
        
        # State
        self.current_group: Optional[GroupInfo] = None
        self._metrics: Dict[str, Any] = {}
        
        logger.info("TgData initialized")
        
    # ==================== Group Management ====================
    
    async def list_groups(self) -> pd.DataFrame:
        """
        List all accessible groups/channels.
        
        Returns:
            DataFrame with group information
        """
        try:
            client = await self.connection_engine.get_client()
            groups_data = []
            
            async with client:
                async for dialog in client.iter_dialogs():
                    if dialog.is_group or dialog.is_channel:
                        entity = dialog.entity
                        
                        group_info = {
                            'GroupID': entity.id,
                            'Title': entity.title,
                            'Username': f"@{entity.username}" if hasattr(entity, 'username') and entity.username else None,
                            'IsChannel': dialog.is_channel,
                            'IsMegagroup': getattr(entity, 'megagroup', False),
                            'ParticipantsCount': getattr(entity, 'participants_count', None)
                        }
                        
                        groups_data.append(group_info)
                        
            df = pd.DataFrame(groups_data)
            logger.info(f"Found {len(df)} groups/channels")
            return df
            
        except Exception as e:
            logger.error(f"Error listing groups: {e}")
            raise
            
    def set_group(self, group_id: int) -> None:
        """
        Set the current group for operations.
        
        Args:
            group_id: Telegram group/channel ID
        """
        self.current_group = GroupInfo(
            id=group_id,
            title="",  # Will be populated on first operation
            username=None
        )
        logger.info(f"Set current group to {group_id}")
        
    # ==================== Message Operations ====================
    
    async def get_messages(self,
                          group_id: Optional[int] = None,
                          limit: Optional[int] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          after_id: int = 0,
                          include_profile_photos: bool = False,
                          with_progress: bool = False,
                          progress_callback: Optional[Callable] = None,
                          batch_size: Optional[int] = None,
                          batch_callback: Optional[Callable] = None,
                          batch_delay: float = 0.0,
                          rate_limit_strategy: str = 'wait') -> pd.DataFrame:
        """
        Get messages from a group with various options.
        
        Args:
            group_id: Target group ID (uses current if not specified)
            limit: Maximum number of messages
            start_date: Get messages after this date
            end_date: Get messages before this date
            after_id: Get messages after this message ID (for incremental extraction)
            include_profile_photos: Whether to download profile photos
            with_progress: Enable progress tracking
            progress_callback: Optional callback for progress updates
            batch_size: If specified, process messages in batches of this size
            batch_callback: Optional async callback called for each batch (batch_df, batch_info)
            batch_delay: Delay in seconds between batches to avoid rate limits (default: 0)
            rate_limit_strategy: How to handle rate limits - 'wait' or 'exponential' (default: 'wait')
            
        Returns:
            DataFrame with messages
        """
        # Use provided group_id or current
        target_group_id = group_id or (self.current_group.id if self.current_group else None)
        if not target_group_id:
            raise ValueError("No group specified. Use set_group() or provide group_id")
            
        # Set as current if different
        if group_id and (not self.current_group or self.current_group.id != group_id):
            self.set_group(group_id)
            
        # Enable progress callback if requested
        if with_progress and not progress_callback:
            def default_progress(current, total, rate):
                if total:
                    percent = (current / total) * 100
                    print(f"\rProgress: {current}/{total} ({percent:.1f}%) - {rate:.1f} msg/s", end="")
                else:
                    print(f"\rProgress: {current} messages - {rate:.1f} msg/s", end="")
                    
            progress_callback = default_progress
            
        # Fetch messages
        df = await self.message_engine.fetch_messages(
            group_id=target_group_id,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            min_id=after_id + 1 if after_id > 0 else None,  # +1 to exclude the after_id message itself
            include_profile_photos=include_profile_photos,
            progress_callback=progress_callback,
            batch_size=batch_size,
            batch_callback=batch_callback,
            batch_delay=batch_delay,
            rate_limit_strategy=rate_limit_strategy
        )
        
        if with_progress:
            print()  # New line after progress
         
        return df
        
        
    async def get_message_count(self, group_id: Optional[int] = None) -> int:
        """
        Get total message count for a group without fetching all messages.
        
        Args:
            group_id: Target group ID (uses current if not specified)
            
        Returns:
            Total message count
        """
        target_group_id = group_id or (self.current_group.id if self.current_group else None)
        if not target_group_id:
            raise ValueError("No group specified")
            
        return await self.message_engine.get_message_count(target_group_id)
        
    async def search_messages(self,
                            query: str,
                            group_id: Optional[int] = None,
                            limit: Optional[int] = None) -> pd.DataFrame:
        """
        Search for messages containing specific text.
        
        Args:
            query: Search query
            group_id: Target group ID (uses current if not specified)
            limit: Maximum number of results
            
        Returns:
            DataFrame with matching messages
        """
        target_group_id = group_id or (self.current_group.id if self.current_group else None)
        if not target_group_id:
            raise ValueError("No group specified")
            
        return await self.message_engine.search_messages(
            group_id=target_group_id,
            query=query,
            limit=limit
        )
        
    # ==================== Message Display and Export ====================
    
    def print_messages(self, 
                      df: pd.DataFrame, 
                      limit: Optional[int] = None,
                      max_length: int = 100) -> None:
        """
        Print messages in a readable format.
        
        Args:
            df: DataFrame with messages
            limit: Maximum number of messages to print
            max_length: Maximum message length to display
        """
        if df.empty:
            print("No messages to display")
            return
            
        messages_to_print = df.head(limit) if limit else df
        
        print(f"\n{'='*80}")
        print(f"Displaying {len(messages_to_print)} of {len(df)} messages")
        print(f"{'='*80}\n")
        
        for _, msg in messages_to_print.iterrows():
            print(format_message_for_display(msg, max_length))
            print(f"{'-'*80}")
            
    def filter_messages(self,
                       df: pd.DataFrame,
                       sender_id: Optional[int] = None,
                       username: Optional[str] = None,
                       keyword: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Filter messages by various criteria.
        
        Args:
            df: Messages DataFrame
            sender_id: Filter by sender ID
            username: Filter by username
            keyword: Filter by message content
            start_date: Filter messages after this date
            end_date: Filter messages before this date
            
        Returns:
            Filtered DataFrame
        """
        # Apply filters
        if sender_id or username:
            df = filter_messages_by_sender(df, sender_id, username)
            
        if keyword:
            df = filter_messages_by_content(df, keyword)
            
        if start_date:
            df = df[df['Date'] >= start_date]
            
        if end_date:
            df = df[df['Date'] <= end_date]
            
        return df
        
    def export_messages(self,
                       df: pd.DataFrame,
                       filepath: str,
                       format: str = 'csv') -> None:
        """
        Export messages to file.
        
        Args:
            df: Messages DataFrame
            filepath: Output file path
            format: Export format ('csv', 'json')
        """
        if format.lower() == 'csv':
            export_to_csv(df, filepath)
        elif format.lower() == 'json':
            export_to_json(df, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    # ==================== Statistics and Metrics ====================
    
    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about messages.
        
        Args:
            df: Messages DataFrame
            
        Returns:
            Dictionary with statistics
        """
        return get_message_statistics(df)
        
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get current session metrics.
        
        Returns:
            Dictionary with metrics
        """
        health_status = await self.connection_engine.health_check()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'current_group': self.current_group.id if self.current_group else None,
            'connection_health': health_status
        }
                
        return metrics
        
    async def export_metrics(self, filepath: str = "telegram_metrics.json") -> None:
        """
        Export session metrics to file.
        
        Args:
            filepath: Output file path
        """
        metrics = await self.get_metrics()
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
            
        logger.info(f"Exported metrics to {filepath}")
        
    # ==================== Utility Methods ====================
    
    async def validate_connection(self) -> bool:
        """
        Validate connection status.
        
        Returns:
            True if connection is valid
        """
        return await self.connection_engine.validate_connection()
        
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Health check results
        """
        return await self.connection_engine.health_check()
        
    def save_photos(self, df: pd.DataFrame, output_dir: str) -> None:
        """
        Save profile photos from messages.
        
        Args:
            df: Messages DataFrame with PhotoData
            output_dir: Directory to save photos
        """
        save_profile_photos(df, output_dir)
        
    async def close(self) -> None:
        """Close all connections."""
        await self.connection_engine.close()
        logger.info("TgData closed")
        
    # ==================== Polling and Real-time Updates ====================
    
    def on_new_message(self, group_id: Optional[int] = None):
        """
        Decorator to register a handler for new messages in real-time.
        Uses Telethon's event system.
        
        Args:
            group_id: Optional group ID to filter messages. If None, receives from all groups.
            
        Example:
            @tg.on_new_message(group_id=12345)
            async def handler(event):
                print(f"New message: {event.message.text}")
        """
        from telethon import events
        
        def decorator(func):
            # Store the handler function for later registration
            if not hasattr(self, '_pending_handlers'):
                self._pending_handlers = []
            
            self._pending_handlers.append((func, group_id))
            logger.info(f"Queued handler for group {group_id or 'all groups'}")
            
            return func
        
        return decorator
    
    async def _register_pending_handlers(self):
        """Register all pending event handlers"""
        if not hasattr(self, '_pending_handlers'):
            return
            
        from telethon import events
        client = await self.connection_engine.get_client()
        
        for func, group_id in self._pending_handlers:
            async def make_handler(f, gid):
                async def wrapped_handler(event):
                    # If group_id specified, filter by it
                    if gid and event.chat_id != gid:
                        return
                    await f(event)
                return wrapped_handler
            
            handler = await make_handler(func, group_id)
            
            if group_id:
                client.add_event_handler(handler, events.NewMessage(chats=group_id))
            else:
                client.add_event_handler(handler, events.NewMessage())
            
            logger.info(f"Registered handler for group {group_id or 'all groups'}")
        
        self._pending_handlers.clear()
    
    async def poll_for_messages(self, 
                               group_id: int,
                               interval: int = 60,
                               after_id: int = 0,
                               callback: Optional[Callable] = None,
                               max_iterations: Optional[int] = None) -> None:
        """
        Poll for new messages at specified intervals.
        
        Args:
            group_id: Group ID to poll messages from
            interval: Polling interval in seconds (default: 60)
            after_id: Message ID to start polling after (default: 0)
            callback: Optional async callback function to process new messages
            max_iterations: Maximum number of polling iterations (None = infinite)
            
        Example:
            async def process_messages(messages_df):
                print(f"Got {len(messages_df)} new messages")
                
            await tg.poll_for_messages(
                group_id=12345,
                interval=30,
                callback=process_messages
            )
        """
        logger.info(f"Starting polling for group {group_id} with interval {interval}s")
        
        current_after_id = after_id
        iterations = 0
        seen_message_ids = set()  # Track all message IDs we've already processed
        
        while max_iterations is None or iterations < max_iterations:
            try:
                # Get new messages since last check
                logger.info(f"Poll iteration {iterations + 1}: Checking for messages after ID {current_after_id}")
                new_messages = await self.get_messages(
                    group_id=group_id,
                    after_id=current_after_id
                )
                
                if not new_messages.empty:
                    # Get all message IDs and filter out already seen ones
                    all_message_ids = new_messages['MessageId'].tolist()
                    new_message_ids = [msg_id for msg_id in all_message_ids if msg_id not in seen_message_ids]
                    
                    if new_message_ids:
                        # Filter DataFrame to only include truly new messages
                        truly_new_messages = new_messages[new_messages['MessageId'].isin(new_message_ids)]
                        
                        # Add new IDs to seen set
                        seen_message_ids.update(new_message_ids)
                        
                        # Simply update to the maximum ID we've seen
                        max_id = max(all_message_ids)
                        logger.info(f"Poll iteration {iterations + 1}: Found {len(truly_new_messages)} new messages, IDs: {sorted(new_message_ids)}")
                        logger.info(f"Updating after_id from {current_after_id} to {max_id}")
                        current_after_id = max_id
                        
                        # Call the callback only with truly new messages
                        if callback:
                            await callback(truly_new_messages)
                    else:
                        # All messages were duplicates, but still update after_id to the max
                        max_id = max(all_message_ids)
                        logger.info(f"Poll iteration {iterations + 1}: Found {len(new_messages)} messages but all were duplicates")
                        logger.info(f"Updating after_id from {current_after_id} to {max_id}")
                        current_after_id = max_id
                else:
                    logger.debug(f"Poll iteration {iterations + 1}: No new messages")
                
                iterations += 1
                
                # Wait for next interval (unless this is the last iteration)
                if max_iterations is None or iterations < max_iterations:
                    await asyncio.sleep(interval)
                    
            except Exception as e:
                logger.error(f"Error during polling: {e}")
                iterations += 1  # Increment even on error to respect max_iterations
                
                # Continue polling after error (unless we've reached max iterations)
                if max_iterations is None or iterations < max_iterations:
                    await asyncio.sleep(interval)
    
    async def run_with_event_loop(self):
        """
        Run the Telegram client with event loop to handle real-time events.
        This method blocks until disconnected.
        
        Example:
            tg = TgData()
            
            @tg.on_new_message()
            async def handler(event):
                print(f"New message: {event.message.text}")
                
            await tg.run_with_event_loop()
        """
        # Register any pending handlers first
        await self._register_pending_handlers()
        
        client = await self.connection_engine.get_client()
        logger.info("Running with event loop. Press Ctrl+C to stop...")
        await client.run_until_disconnected()
        
    # ==================== Context Manager Support ====================
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Example usage
if __name__ == "__main__":
    async def main():
        # Simple usage
        tg = TgData()
        
        # List groups
        groups = await tg.list_groups()
        print(f"Found {len(groups)} groups")
        
        if not groups.empty:
            # Select first group
            group_id = groups.iloc[0]['GroupID']
            tg.set_group(group_id)
            
            # Get recent messages with progress
            messages = await tg.get_messages(
                limit=100,
                with_progress=True
            )
            
            # Display messages
            tg.print_messages(messages, limit=10)
            
            # Get statistics
            stats = tg.get_statistics(messages)
            print(f"\nStatistics: {stats}")
            
            # Export
            tg.export_messages(messages, "messages.csv")
            
    asyncio.run(main())