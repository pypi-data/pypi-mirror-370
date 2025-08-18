"""
Smoke tests for polling and real-time message features
"""
# To run: python -m tgdata.smoke_tests.test_06_polling_simple

import asyncio
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import pandas as pd


async def test_polling_basic():
    """Test basic polling functionality"""
    print("TEST: Basic polling functionality...")
    
    try:
        # Initialize TgData
        tg = TgData("config.ini")
        
        # Get a test group
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available for testing")
            return False
        
        
        
        # test_group_id=2367653179
        test_group_id=4611400320
        print(f"Testing with group ID: {test_group_id}")
        
        # Define a callback to handle new messages
        messages_received = []
        
        async def message_callback(messages_df):
            count = len(messages_df)
            messages_received.append(count)
            print(f"  Received {count} new messages")
            if not messages_df.empty:
                # Show first message
                first_msg = messages_df.iloc[0]
                msg_text = first_msg.get('Message', 'No text')[:50]
                print(f"  First message: {msg_text}...")
                # Debug: show message IDs and content
                print(f"  Message IDs: {messages_df['MessageId'].tolist()}")
                print(f"  Max ID: {messages_df['MessageId'].max()}")
                # Show all messages
                for idx, row in messages_df.iterrows():
                    print(f"    - ID {row['MessageId']}: {row['Message'][:20]}...")
        
        # Get the latest message ID to start polling after
        initial_messages = await tg.get_messages(group_id=test_group_id, limit=1)
        start_after_id = 0
        if not initial_messages.empty:
            start_after_id = initial_messages['MessageId'].max()
            print(f"Starting polling after message ID: {start_after_id}")
            print(f"Latest message: {initial_messages.iloc[0]['Message'][:20]}...")
        
        # Test polling with 3 iterations
        print("\nPolling for 3 iterations (5 seconds each)...")
        await tg.poll_for_messages(
            group_id=test_group_id,
            interval=5,
            after_id=start_after_id,
            callback=message_callback,
            max_iterations=4
        )
        
        print(f"✓ Polling completed. Total polls that found messages: {len(messages_received)}")
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Polling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False




async def main():
    """Run polling test"""
    print("Polling Test")
    print("=" * 50)
    
    tests = [
        test_polling_basic,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\nSummary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All polling tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)