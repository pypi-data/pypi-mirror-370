"""
Test: Get All Messages in Batches
Demonstrates extracting messages in batches and appending to CSV
"""

# to run python -m tgdata.smoke_tests.test_03_get_all_messages_in_batches

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData


async def test_get_all_messages_in_batches():
    """Get messages in batches and save to CSV"""
    
    # Configuration
    group_id = int(os.environ.get('TEST_GROUP_ID', '1670178185'))  # Bitcoinsensus by default
    output_csv = 'all_messages_merged_batches.csv'
    batch_size = 10
    num_batches = 3
    
    print(f"Getting messages from group {group_id} in batches")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {num_batches}")
    print(f"Output file: {output_csv}")
    print("-" * 50)
    
    # Remove existing file if exists
    if os.path.exists(output_csv):
        os.remove(output_csv)
        print(f"Removed existing {output_csv}")
    
    try:
        # Initialize TgData
        tg = TgData("config.ini")
        
        last_message_id = 0
        total_messages = 0
        
        # Process in batches
        for batch_num in range(1, num_batches + 1):
            print(f"\nBatch {batch_num}/{num_batches}:")
            print(f"  Getting messages after ID {last_message_id}...")
            
            # Get batch of messages
            batch = await tg.get_messages(
                group_id=group_id,
                after_id=last_message_id,
                limit=batch_size
            )
            
            if not batch.empty:
                # Write to CSV (append mode after first batch)
                if batch_num == 1:
                    batch.to_csv(output_csv, index=False)
                else:
                    batch.to_csv(output_csv, mode='a', header=False, index=False)
                
                # Update counters
                batch_count = len(batch)
                total_messages += batch_count
                last_message_id = int(batch['MessageId'].max())
                
                print(f"  Saved {batch_count} messages")
                print(f"  Last message ID: {last_message_id}")
            else:
                print(f"  No messages found")
                break
        
        print(f"\n✅ Total messages saved: {total_messages}")
        print(f"📁 Output file: {output_csv}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await tg.close()


async def main():
    """Run the test"""
    print("Test: Get All Messages in Batches")
    print("-" * 40)
    
    success = await test_get_all_messages_in_batches()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())