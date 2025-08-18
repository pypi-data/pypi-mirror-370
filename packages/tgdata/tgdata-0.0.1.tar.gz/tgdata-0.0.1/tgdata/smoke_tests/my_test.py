import asyncio
import os
import sys
import pandas as pd
from tgdata import TgData

# python -m tgdata.smoke_tests.my_test



async def extract_to_csv_with_resume(tg: TgData, group_id: int, csv_file: str = "messages.csv", batch_size: int = 10):
    """
    Extract messages to CSV using the CSV itself as checkpoint.
    Supports resuming from the last message ID in the CSV.
    
    Uses get_messages(after_id=...) for incremental extraction.
    """
    # Read last message ID from existing CSV
    last_message_id = 0
    existing_count = 0
    
    if os.path.exists(csv_file):
        try:
            # Read just the last row efficiently
            # In production, you might use: pd.read_csv(csv_file, skiprows=lambda x: x < last_row)
            df_existing = pd.read_csv(csv_file)
            if not df_existing.empty:
                # Get the maximum message ID (in case CSV is not ordered)
                last_message_id = int(df_existing['MessageId'].max())
                existing_count = len(df_existing)
                print(f"📄 Found existing CSV with {existing_count} messages")
                print(f"📍 Resuming from message ID: {last_message_id}")
        except Exception as e:
            print(f"⚠️  Could not read existing CSV: {e}")
            print("   Starting fresh extraction")
    else:
        print("📄 No existing CSV found, starting fresh extraction")
    
    # Use get_messages with after_id for incremental extraction
    print(f"\n🔄 Extracting messages since ID {last_message_id}...")
    
    # Get today's date at midnight in UTC
    from datetime import datetime, time, timezone
    today_utc = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
    print(f"📅 Filtering for messages from today ({today_utc.date()}) only")
    print(f"⏰ Start time filter: {today_utc} (UTC)")
    print(f"⏰ Current time: {datetime.now(timezone.utc)} (UTC)")
    
    try:
        # Use get_messages with after_id for proper batch extraction
        new_messages = await tg.get_messages(
            group_id=group_id,
            after_id=last_message_id
        )
        
        # For demo purposes, limit to batch_size and filter for today
        if not new_messages.empty:
            print(f"   Got {len(new_messages)} messages since ID {last_message_id}")
            
            # Convert Date column to UTC if needed
            new_messages['Date'] = pd.to_datetime(new_messages['Date'], utc=True)
            
            # Filter for today's messages only (for demo)
            today_messages = new_messages[new_messages['Date'] >= today_utc]
            print(f"   Found {len(today_messages)} messages from today")
            
            # Limit to batch_size
            new_messages = today_messages.head(batch_size)
            print(f"   Limited to {len(new_messages)} messages (batch_size={batch_size})")
        
        if not new_messages.empty:
            # Sort by MessageId to ensure order
            new_messages = new_messages.sort_values('MessageId')
            
            # Append to CSV
            new_messages.to_csv(
                csv_file,
                mode='a',
                header=not os.path.exists(csv_file),
                index=False
            )
            
            print(f"✅ Added {len(new_messages)} new messages to CSV")
            
            # Show sample of new messages
            print("\n📋 Sample of new messages:")
            # Show relevant columns
            cols_to_show = ['MessageId', 'Name', 'Date']
            print(new_messages[cols_to_show].head(5))
        else:
            print("ℹ️  No new messages found")
    
    except Exception as e:
        print(f"❌ Error extracting messages: {e}")
        new_messages = pd.DataFrame()
    
    # Summary
    print(f"\n📊 Extraction Summary:")
    print(f"   - Existing messages: {existing_count}")
    print(f"   - New messages: {len(new_messages) if not new_messages.empty else 0}")
    print(f"   - Total messages: {existing_count + (len(new_messages) if not new_messages.empty else 0)}")
    
    return new_messages



async def main():
    """Run CSV checkpoint test"""
    
    
    print("This test demonstrates:")
    print("- Using CSV file itself as checkpoint (no checkpoint.json)")
    print("- Reading last message ID from existing CSV")
    print("- Resuming extraction from that point")
    print("- Appending new messages to existing CSV")
    
    # Define the test function inline or import it
    # For now, let's create a simple test
    tg = TgData("config.ini")
    csv_file = "test_messages.csv"
    
    try:
        # Get test group ID from environment or use Bitcoinsensus channel
        group_id = int(os.environ.get('TEST_GROUP_ID', '1670178185'))  # Bitcoinsensus channel
        
        print(f"Using group ID: {group_id}")
        print("\n⚠️  Using gentle settings: batch_size=10, only today's messages")
        
        # Run the extraction
        messages = await extract_to_csv_with_resume(tg, group_id, csv_file, batch_size=10)
        
        success = True
    except Exception as e:
        print(f"Error: {e}")
        success = False
    finally:
        await tg.close()
        # Cleanup
        if os.path.exists(csv_file):
            os.remove(csv_file)
            print(f"Cleaned up {csv_file}")
    

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())