"""
tgdata - Telegram Data Extraction Library

A production-grade Python library for extracting and processing Telegram group and channel messages.
"""

# Main class
from .tgdata import TgData

# Models
from .models import (
    MessageData,
    GroupInfo,
    ConnectionConfig,
    RateLimitInfo
)

# Utilities
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

# Progress tracking
from .progress import ProgressTracker

__version__ = "0.0.0"

__all__ = [
    # Main class
    "TgData",
    
    # Models
    "MessageData",
    "GroupInfo",
    "ConnectionConfig",
    "RateLimitInfo",
    
    # Utilities
    "format_message_for_display",
    "export_to_json",
    "export_to_csv",
    "filter_messages_by_sender",
    "filter_messages_by_content",
    "get_message_statistics",
    "save_profile_photos",
    "create_metrics_report",
    
    # Progress
    "ProgressTracker"
]