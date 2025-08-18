"""
Utility functions for the Telegram Group Message Crawler.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def format_message_for_display(message: Dict[str, Any], max_length: int = 100) -> str:
    """
    Format a message for display.
    
    Args:
        message: Message dictionary
        max_length: Maximum message length to display
        
    Returns:
        Formatted message string
    """
    msg_text = message.get('Message', '')
    if msg_text and len(msg_text) > max_length:
        msg_text = f"{msg_text[:max_length]}..."
        
    return (
        f"{message.get('Date', 'Unknown date')} | "
        f"{message.get('Name', 'Unknown')} "
        f"({message.get('Username', 'No username')}): "
        f"{msg_text or '[No text]'}"
    )


def export_to_json(df: pd.DataFrame, filepath: str, pretty: bool = True) -> None:
    """
    Export DataFrame to JSON file.
    
    Args:
        df: DataFrame to export
        filepath: Output file path
        pretty: Whether to pretty-print JSON
    """
    try:
        # Convert DataFrame to dict, handling datetime objects
        data = df.to_dict('records')
        
        # Convert datetime objects to strings
        for record in data:
            for key, value in record.items():
                if isinstance(value, datetime):
                    record[key] = value.isoformat()
                elif isinstance(value, bytes):
                    # Don't include binary data in JSON
                    record[key] = "[Binary data]"
                    
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
                
        logger.info(f"Exported {len(df)} messages to {filepath}")
        
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise


def export_to_csv(df: pd.DataFrame, filepath: str) -> None:
    """
    Export DataFrame to CSV file.
    
    Args:
        df: DataFrame to export
        filepath: Output file path
    """
    try:
        # Remove binary data columns for CSV export
        export_df = df.copy()
        if 'PhotoData' in export_df.columns:
            export_df = export_df.drop('PhotoData', axis=1)
            
        export_df.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"Exported {len(df)} messages to {filepath}")
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise


def filter_messages_by_sender(df: pd.DataFrame, sender_id: Optional[int] = None, 
                            username: Optional[str] = None) -> pd.DataFrame:
    """
    Filter messages by sender.
    
    Args:
        df: Messages DataFrame
        sender_id: Sender ID to filter by
        username: Username to filter by
        
    Returns:
        Filtered DataFrame
    """
    if sender_id:
        df = df[df['SenderId'] == sender_id]
    elif username:
        df = df[df['Username'].str.contains(username, case=False, na=False)]
        
    return df


def filter_messages_by_content(df: pd.DataFrame, keyword: str, 
                             case_sensitive: bool = False) -> pd.DataFrame:
    """
    Filter messages containing specific keyword.
    
    Args:
        df: Messages DataFrame
        keyword: Keyword to search for
        case_sensitive: Whether search is case sensitive
        
    Returns:
        Filtered DataFrame
    """
    return df[df['Message'].str.contains(
        keyword, 
        case=case_sensitive, 
        na=False
    )]


def get_message_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get statistics about messages.
    
    Args:
        df: Messages DataFrame
        
    Returns:
        Dictionary with statistics
    """
    if df.empty:
        return {
            'total_messages': 0,
            'unique_senders': 0,
            'date_range': None,
            'top_senders': []
        }
        
    stats = {
        'total_messages': len(df),
        'unique_senders': df['SenderId'].nunique(),
        'date_range': {
            'start': df['Date'].min(),
            'end': df['Date'].max()
        },
        'messages_with_text': df['Message'].notna().sum(),
        'replies': df['ReplyToId'].notna().sum(),
        'forwards': df['ForwardedFrom'].notna().sum()
    }
    
    # Top senders
    top_senders = df.groupby(['SenderId', 'Name']).size().sort_values(
        ascending=False
    ).head(10)
    
    stats['top_senders'] = [
        {
            'sender_id': sender_id,
            'name': name,
            'message_count': count
        }
        for (sender_id, name), count in top_senders.items()
    ]
    
    return stats


def save_profile_photos(df: pd.DataFrame, output_dir: str) -> None:
    """
    Save profile photos from messages to directory.
    
    Args:
        df: Messages DataFrame with PhotoData column
        output_dir: Directory to save photos
    """
    if 'PhotoData' not in df.columns:
        logger.warning("No PhotoData column in DataFrame")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    saved_count = 0
    
    for _, row in df.iterrows():
        if row['PhotoData'] is not None:
            filename = f"{row['SenderId']}_{row['Username'].replace('@', '')}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            try:
                with open(filepath, 'wb') as f:
                    f.write(row['PhotoData'])
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving photo for {row['SenderId']}: {e}")
                
    logger.info(f"Saved {saved_count} profile photos to {output_dir}")


def create_metrics_report(df: pd.DataFrame, group_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a comprehensive metrics report.
    
    Args:
        df: Messages DataFrame
        group_info: Information about the group
        
    Returns:
        Dictionary with metrics
    """
    stats = get_message_statistics(df)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'group': group_info,
        'statistics': stats,
        'processing_info': {
            'total_processed': len(df),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        }
    }
    
    # Add time-based statistics if we have data
    if not df.empty:
        df['Hour'] = pd.to_datetime(df['Date']).dt.hour
        df['DayOfWeek'] = pd.to_datetime(df['Date']).dt.day_name()
        
        report['time_analysis'] = {
            'messages_by_hour': df['Hour'].value_counts().sort_index().to_dict(),
            'messages_by_day': df['DayOfWeek'].value_counts().to_dict()
        }
        
    return report