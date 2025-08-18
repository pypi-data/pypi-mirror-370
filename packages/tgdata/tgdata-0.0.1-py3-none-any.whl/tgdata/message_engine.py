"""
Message processing engine for Telegram.
Handles message fetching, filtering, deduplication, and formatting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
import pandas as pd
from telethon.errors import FloodWaitError

from .connection_engine import ConnectionEngine
from .models import MessageData
from .progress import ProgressTracker

logger = logging.getLogger(__name__)


class MessageEngine:
    """
    Handles all message-related operations.
    """
    
    def __init__(self,
                 connection_engine: ConnectionEngine):
        """
        Initialize message engine.
        
        Args:
            connection_engine: Connection engine instance
        """
        self.connection_engine = connection_engine
        
    async def fetch_messages(self,
                           group_id: int,
                           limit: Optional[int] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           include_profile_photos: bool = False,
                           progress_callback: Optional[Callable] = None,
                           min_id: Optional[int] = None,
                           batch_size: Optional[int] = None,
                           batch_callback: Optional[Callable] = None,
                           batch_delay: float = 0.0,
                           rate_limit_strategy: str = 'wait') -> pd.DataFrame:
        """
        Fetch messages from a group with various filters.
        
        Args:
            group_id: Telegram group/channel ID
            limit: Maximum number of messages to fetch
            start_date: Get messages after this date
            end_date: Get messages before this date
            include_profile_photos: Whether to download profile photos
            progress_callback: Optional callback for progress updates
            min_id: Minimum message ID (for resuming)
            batch_size: If specified, process messages in batches of this size
            batch_callback: Optional async callback called for each batch (batch_df, batch_info)
            batch_delay: Delay in seconds between batches to avoid rate limits (default: 0)
            rate_limit_strategy: How to handle rate limits - 'wait' or 'exponential' (default: 'wait')
            
        Returns:
            DataFrame with messages
        """
        # Set up progress tracking
        progress_tracker = None
        if progress_callback:
            progress_tracker = ProgressTracker(
                total_expected=limit,
                callback=progress_callback
            )
            progress_tracker.start()
            
        messages_data = []
        processed_count = 0
        batch_count = 0
        
        # Set up batching if requested
        batch_messages = []
        effective_batch_size = batch_size if batch_size and batch_callback else None
        
        try:
            client = await self.connection_engine.get_client()
            
            async with client:
                # Get the entity
                channel = await client.get_entity(group_id)
                logger.info(f"Fetching messages from: {channel.title}")
                
                # Determine iteration parameters
                offset_date = end_date if end_date else datetime.now()
                reverse = bool(start_date)  # Reverse if we have a start date
                
                # Build kwargs for iter_messages
                iter_kwargs = {
                    'entity': channel,
                    'limit': limit if limit else 100,  # Default limit for polling
                    'offset_date': offset_date,
                    'reverse': reverse
                }
                
                # Only add min_id if it's not None
                if min_id is not None:
                    # Since min_id includes the ID itself (>= behavior), we already adjusted it in tgdata.py
                    iter_kwargs['min_id'] = min_id
                    # When using min_id (for polling), we want chronological order
                    iter_kwargs['reverse'] = True
                    # Remove offset_date when using min_id to avoid conflicts
                    iter_kwargs.pop('offset_date', None)
                    logger.info(f"Polling with min_id={min_id}, limit={iter_kwargs.get('limit', 'no limit')}")
                
                # Track the original min_id to filter duplicates
                original_min_id = min_id - 1 if min_id else None
                
                # Iterate through messages
                async for msg in client.iter_messages(**iter_kwargs):
                    # Skip messages we've already seen (when polling)
                    if original_min_id is not None and msg.id <= original_min_id:
                        logger.info(f"Skipping already-seen message {msg.id} <= {original_min_id}")
                        continue
                    
                    # Log messages we're processing
                    if min_id is not None:
                        logger.info(f"Processing message {msg.id} (min_id was {min_id}, original_min_id was {original_min_id})")
                        
                    # Apply date filters
                    if start_date and msg.date < start_date:
                        continue
                    if end_date and msg.date > end_date:
                        break
                        
                            
                    # Process message
                    message_data = await self._process_message(
                        msg, 
                        client,
                        include_profile_photos
                    )
                    
                    if message_data:
                        messages_data.append(message_data.to_dict())
                        
                        # Handle batch processing
                        if effective_batch_size:
                            batch_messages.append(message_data.to_dict())
                            
                            # Process batch when it reaches the size
                            if len(batch_messages) >= effective_batch_size:
                                batch_count += 1
                                batch_df = pd.DataFrame(batch_messages)
                                batch_info = {
                                    'batch_num': batch_count,
                                    'batch_size': len(batch_messages),
                                    'total_processed': processed_count + len(batch_messages),
                                    'group_id': group_id
                                }
                                
                                # Call the batch callback
                                await batch_callback(batch_df, batch_info)
                                
                                # Clear batch buffer
                                batch_messages = []
                                
                                # Apply batch delay to avoid rate limits
                                if batch_delay > 0:
                                    logger.info(f"Waiting {batch_delay}s between batches to avoid rate limits...")
                                    await asyncio.sleep(batch_delay)
                            
                        processed_count += 1
                        
                        # Update progress
                        if progress_tracker:
                            progress_tracker.update()
                            
                        # Log progress
                        if processed_count % 100 == 0:
                            logger.info(f"Processed {processed_count} messages...")
                            
                # Process final batch if there are remaining messages
                if effective_batch_size and batch_messages:
                    batch_count += 1
                    batch_df = pd.DataFrame(batch_messages)
                    batch_info = {
                        'batch_num': batch_count,
                        'batch_size': len(batch_messages),
                        'total_processed': processed_count,
                        'group_id': group_id,
                        'is_final': True
                    }
                    await batch_callback(batch_df, batch_info)
                            
        except FloodWaitError as e:
            await self.connection_engine.handle_rate_limit(e, client, strategy=rate_limit_strategy)
            # Retry after rate limit
            return await self.fetch_messages(
                group_id=group_id,
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                include_profile_photos=include_profile_photos,
                progress_callback=progress_callback,
                min_id=min_id,
                batch_size=batch_size,
                batch_callback=batch_callback
            )
            
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            raise
            
        # Create DataFrame
        df = pd.DataFrame(messages_data)
        
        # Sort by MessageId when using min_id (for polling)
        if min_id is not None and not df.empty:
            df = df.sort_values('MessageId', ascending=True)
            
        logger.info(f"Retrieved {len(df)} messages")
        
            
        return df
        
    async def _process_message(self,
                             msg,
                             client,
                             include_profile_photos: bool) -> Optional[MessageData]:
        """Process a single message"""
        try:
            sender = await msg.get_sender()
            if not sender:
                return None
                
            # Extract sender info
            sender_name = f"{getattr(sender, 'first_name', '') or ''} {getattr(sender, 'last_name', '') or ''}".strip()
            username = f"@{sender.username}" if hasattr(sender, 'username') and sender.username else "No username"
            
            # Create message data
            message_data = MessageData(
                message_id=msg.id,
                sender_id=sender.id,
                sender_name=sender_name,
                username=username,
                message=msg.message,
                date=msg.date,
                reply_to_id=msg.reply_to_msg_id,
                forwarded_from=msg.fwd_from.from_id if msg.fwd_from else None
            )
            
            # Download profile photo if requested
            if include_profile_photos and hasattr(sender, 'photo') and sender.photo:
                try:
                    photo_bytes = await client.download_profile_photo(sender, file=bytes)
                    message_data.photo_data = photo_bytes
                except Exception as e:
                    logger.warning(f"Failed to download photo for {sender.id}: {e}")
                    
            return message_data
            
        except Exception as e:
            logger.error(f"Error processing message {msg.id}: {e}")
            return None
            
        
            
    async def get_message_count(self, group_id: int) -> int:
        """
        Get total message count for a group.
        
        Args:
            group_id: Telegram group/channel ID
            
        Returns:
            Total message count
        """
        try:
            client = await self.connection_engine.get_client()
            
            async with client:
                # Get the messages with limit=1 to access count
                messages = await client.get_messages(group_id, limit=1)
                
                # TotalList objects have a 'total' attribute
                if hasattr(messages, 'total'):
                    return messages.total
                else:
                    # If it's just a regular list, we can't get total efficiently
                    logger.warning("Could not get message count efficiently")
                    return 0
                    
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            raise
            
    async def search_messages(self,
                            group_id: int,
                            query: str,
                            limit: Optional[int] = None) -> pd.DataFrame:
        """
        Search for messages containing specific text.
        
        Args:
            group_id: Telegram group/channel ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            DataFrame with matching messages
        """
        try:
            client = await self.connection_engine.get_client()
            messages_data = []
            
            async with client:
                channel = await client.get_entity(group_id)
                
                async for msg in client.iter_messages(
                    channel,
                    search=query,
                    limit=limit
                ):
                    message_data = await self._process_message(msg, client, False)
                    if message_data:
                        messages_data.append(message_data.to_dict())
                        
            df = pd.DataFrame(messages_data)
            logger.info(f"Found {len(df)} messages matching '{query}'")
            return df
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            raise