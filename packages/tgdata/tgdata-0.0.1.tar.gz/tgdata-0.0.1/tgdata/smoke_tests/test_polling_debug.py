"""
Debug test for polling to understand message retrieval issues
"""
# To run: python -m tgdata.smoke_tests.test_polling_debug

import asyncio
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import pandas as pd
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_polling_debug():
    """Debug polling to understand message retrieval"""
    print("=" * 60)
    print("DEBUG: Polling Message Retrieval")
    print("=" * 60)
    
    try:
        # Initialize TgData
        tg = TgData("config.ini")
        
        # Use specific test group
        test_group_id = 4611400320
        print(f"Testing with group ID: {test_group_id}")
        
        # Get all current messages to establish baseline
        print("\n1. Getting ALL messages to establish baseline...")
        all_messages = await tg.get_messages(group_id=test_group_id, limit=50)
        if not all_messages.empty:
            print(f"   Total messages in group: {len(all_messages)}")
            print(f"   Latest 5 message IDs: {sorted(all_messages['MessageId'].tolist())[-5:]}")
            latest_id = all_messages['MessageId'].max()
            print(f"   Latest message ID: {latest_id}")
            print(f"   Latest message: {all_messages[all_messages['MessageId'] == latest_id]['Message'].iloc[0][:50]}...")
        
        print("\n2. Now send some test messages to the group and press Enter when done...")
        input("   Press Enter after sending messages: ")
        
        # Get messages again to see what was added
        print("\n3. Getting ALL messages again to see what was added...")
        all_messages_after = await tg.get_messages(group_id=test_group_id, limit=50)
        new_message_ids = set(all_messages_after['MessageId']) - set(all_messages['MessageId'])
        
        if new_message_ids:
            print(f"   New message IDs found: {sorted(new_message_ids)}")
            for msg_id in sorted(new_message_ids):
                msg_row = all_messages_after[all_messages_after['MessageId'] == msg_id].iloc[0]
                print(f"     - ID {msg_id}: {msg_row['Message'][:30]}...")
        else:
            print("   No new messages found")
        
        # Now test getting messages with after_id
        print(f"\n4. Testing get_messages with after_id={latest_id}...")
        messages_after_id = await tg.get_messages(
            group_id=test_group_id,
            after_id=latest_id
        )
        
        if not messages_after_id.empty:
            print(f"   Found {len(messages_after_id)} messages after ID {latest_id}")
            print(f"   Message IDs: {sorted(messages_after_id['MessageId'].tolist())}")
            for _, row in messages_after_id.iterrows():
                print(f"     - ID {row['MessageId']}: {row['Message'][:30]}...")
        else:
            print(f"   No messages found after ID {latest_id}")
        
        # Compare what we should have found vs what we actually found
        print("\n5. Analysis:")
        if new_message_ids:
            found_ids = set(messages_after_id['MessageId'].tolist()) if not messages_after_id.empty else set()
            missing_ids = new_message_ids - found_ids
            if missing_ids:
                print(f"   ⚠️  MISSING MESSAGE IDs: {sorted(missing_ids)}")
                print("   These messages exist but weren't returned by after_id query!")
            else:
                print("   ✓ All new messages were correctly retrieved with after_id")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sequential_polling():
    """Test sequential message fetching to understand timing"""
    print("\n" + "=" * 60)
    print("DEBUG: Sequential Polling Test")
    print("=" * 60)
    
    try:
        tg = TgData("config.ini")
        test_group_id = 4611400320
        
        print(f"Testing with group ID: {test_group_id}")
        
        # Get initial state
        initial = await tg.get_messages(group_id=test_group_id, limit=1)
        start_id = initial['MessageId'].max() if not initial.empty else 0
        print(f"Starting after message ID: {start_id}")
        
        print("\nNow I will poll 5 times with 3-second intervals.")
        print("Send messages during this time to test detection.\n")
        
        all_found_messages = []
        current_after_id = start_id
        
        for i in range(5):
            print(f"Poll {i+1}: Checking for messages after ID {current_after_id}...")
            
            # Get new messages
            new_messages = await tg.get_messages(
                group_id=test_group_id,
                after_id=current_after_id
            )
            
            if not new_messages.empty:
                msg_ids = sorted(new_messages['MessageId'].tolist())
                print(f"  Found {len(new_messages)} messages: IDs {msg_ids}")
                
                # Check for gaps in message IDs
                if len(msg_ids) > 1:
                    for j in range(len(msg_ids) - 1):
                        if msg_ids[j+1] - msg_ids[j] > 1:
                            print(f"  ⚠️  GAP detected: Missing ID(s) between {msg_ids[j]} and {msg_ids[j+1]}")
                
                # Update after_id
                new_max_id = new_messages['MessageId'].max()
                print(f"  Updating after_id from {current_after_id} to {new_max_id}")
                current_after_id = new_max_id
                
                all_found_messages.extend(msg_ids)
            else:
                print(f"  No new messages")
            
            if i < 4:  # Don't sleep after last iteration
                await asyncio.sleep(3)
        
        # Final check - get all messages to see if we missed any
        print("\nFinal verification - checking for any missed messages...")
        final_messages = await tg.get_messages(
            group_id=test_group_id,
            after_id=start_id
        )
        
        if not final_messages.empty:
            all_actual_ids = set(final_messages['MessageId'].tolist())
            found_ids = set(all_found_messages)
            missed_ids = all_actual_ids - found_ids
            
            if missed_ids:
                print(f"⚠️  MISSED MESSAGES: {sorted(missed_ids)}")
                print("These messages exist but were not detected during polling!")
            else:
                print("✓ All messages were successfully detected during polling")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Sequential test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run debug tests"""
    tests = [
        test_polling_debug,
        test_sequential_polling
    ]
    
    for test in tests:
        await test()
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())