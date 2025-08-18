"""
Data models for the Telegram Group Message Crawler.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Dict



@dataclass
class RateLimitInfo:
    """Track rate limit information"""
    requests_made: int = 0
    window_start: float = 0
    last_request: float = 0
    flood_wait_until: float = 0


@dataclass
class GroupInfo:
    """Information about a Telegram group/channel"""
    id: int
    title: str
    username: Optional[str] = None
    is_channel: bool = False
    is_megagroup: bool = False
    participants_count: Optional[int] = None


@dataclass
class MessageData:
    """Structured message data"""
    message_id: int
    sender_id: int
    sender_name: str
    username: str
    message: Optional[str]
    date: datetime
    reply_to_id: Optional[int] = None
    forwarded_from: Optional[int] = None
    photo_data: Optional[bytes] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame creation"""
        return {
            'MessageId': self.message_id,
            'SenderId': self.sender_id,
            'Name': self.sender_name,
            'Username': self.username,
            'Message': self.message,
            'Date': self.date,
            'ReplyToId': self.reply_to_id,
            'ForwardedFrom': self.forwarded_from,
            'PhotoData': self.photo_data
        }


@dataclass
class ConnectionConfig:
    """Configuration for Telegram connection"""
    api_id: str
    api_hash: str
    session_file: str
    phone: Optional[str] = None
    username: Optional[str] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True