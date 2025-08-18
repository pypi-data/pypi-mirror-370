"""
Smoke test for progress tracking feature
"""
# To run: python -m tgdata.smoke_tests.test_05_with_progress_feature

import asyncio
import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import pandas as pd


async def test_default_progress():
    """Test with default progress display"""
    print("TEST: Default progress tracking...")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        # Get groups
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available for testing")
            return False
            
        # Select a group with decent number of messages
        test_group = None
        for _, group in groups.iterrows():
            if group['ParticipantsCount'] and group['ParticipantsCount'] > 10:
                test_group = group
                break
        
        if test_group is None:
            test_group = groups.iloc[0]
            
        print(f"Using group: {test_group['Title']} (ID: {test_group['GroupID']})")
        print(f"Participants: {test_group.get('ParticipantsCount', 'Unknown')}")
        print("\nFetching messages with default progress display...")
        print("-" * 50)
        
        # Fetch with default progress
        start_time = time.time()
        messages = await tg.get_messages(
            group_id=int(test_group['GroupID']),
            limit=100,
            with_progress=True  # This enables default progress display
        )
        elapsed = time.time() - start_time
        
        print(f"\n✓ Fetched {len(messages)} messages in {elapsed:.2f} seconds")
        print(f"✓ Average rate: {len(messages)/elapsed:.1f} messages/second")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Default progress test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_custom_progress_callback():
    """Test with custom progress callback"""
    print("\n\nTEST: Custom progress callback...")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        # Get first group
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
            
        test_group = groups.iloc[0]
        print(f"Using group: {test_group['Title']}")
        
        # Track progress data
        progress_data = []
        
        def custom_callback(current, total, rate):
            progress_data.append({
                'current': current,
                'total': total,
                'rate': rate,
                'time': time.time()
            })
            
            # Custom display
            if total:
                bar_length = 40
                filled = int(bar_length * current / total)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r[{bar}] {current}/{total} @ {rate:.1f} msg/s", end="")
            else:
                print(f"\rFetched: {current} messages @ {rate:.1f} msg/s", end="")
        
        print("\nFetching with custom progress bar...")
        print("-" * 50)
        
        messages = await tg.get_messages(
            group_id=int(test_group['GroupID']),
            limit=150,
            with_progress=True,
            progress_callback=custom_callback
        )
        
        print(f"\n\n✓ Custom callback was called {len(progress_data)} times")
        
        if progress_data:
            # Analyze progress data
            rates = [d['rate'] for d in progress_data if d['rate'] > 0]
            if rates:
                print(f"✓ Rate statistics:")
                print(f"  - Min rate: {min(rates):.1f} msg/s")
                print(f"  - Max rate: {max(rates):.1f} msg/s")
                print(f"  - Avg rate: {sum(rates)/len(rates):.1f} msg/s")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Custom callback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progress_with_different_limits():
    """Test progress tracking with different message limits"""
    print("\n\nTEST: Progress with different limits...")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
            
        test_group = groups.iloc[0]
        print(f"Using group: {test_group['Title']}")
        
        # Test different limits
        limits = [10, 50, 200]
        
        for limit in limits:
            print(f"\nTesting with limit={limit}:")
            
            # Simple callback to track if it's working
            callback_count = 0
            
            def counting_callback(current, total, rate):
                nonlocal callback_count
                callback_count += 1
                # Update every 10 messages or at the end
                if current % 10 == 0 or current == total:
                    print(f"  Progress: {current}/{total if total else '?'} messages")
            
            messages = await tg.get_messages(
                group_id=int(test_group['GroupID']),
                limit=limit,
                with_progress=True,
                progress_callback=counting_callback
            )
            
            print(f"  ✓ Retrieved {len(messages)} messages")
            print(f"  ✓ Callback invoked {callback_count} times")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Different limits test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progress_without_callback():
    """Test with_progress=True but no callback (uses default)"""
    print("\n\nTEST: Progress without custom callback...")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
            
        test_group = groups.iloc[0]
        print(f"Using group: {test_group['Title']}")
        print("\nThis should show the default progress display:")
        print("-" * 50)
        
        # Just with_progress=True, no callback
        messages = await tg.get_messages(
            group_id=int(test_group['GroupID']),
            limit=75,
            with_progress=True  # Default progress display
        )
        
        print(f"\n✓ Successfully fetched {len(messages)} messages")
        print("✓ Default progress display should have appeared above")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progress_with_date_filter():
    """Test progress tracking with date filters"""
    print("\n\nTEST: Progress with date filtering...")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
            
        test_group = groups.iloc[0]
        print(f"Using group: {test_group['Title']}")
        
        # Get messages from last 30 days with progress
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=30)
        
        print(f"\nFetching messages from last 30 days...")
        print(f"Start date: {start_date.strftime('%Y-%m-%d')}")
        print("-" * 50)
        
        # Track progress stages
        stages = []
        
        def stage_callback(current, total, rate):
            stage = f"{current}/{total if total else '?'}"
            if not stages or stages[-1] != stage:
                stages.append(stage)
            
            # Show progress every 25 messages
            if current % 25 == 0:
                print(f"  Downloaded {current} messages from last 30 days...")
        
        messages = await tg.get_messages(
            group_id=int(test_group['GroupID']),
            start_date=start_date,
            limit=100,
            with_progress=True,
            progress_callback=stage_callback
        )
        
        print(f"\n✓ Found {len(messages)} messages from last 30 days")
        print(f"✓ Progress went through {len(stages)} update stages")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Date filter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all progress tracking tests"""
    print("Progress Tracking Feature Tests")
    print("=" * 70)
    print("\nThese tests demonstrate the progress tracking feature.")
    print("You should see various progress displays during message fetching.\n")
    
    tests = [
        test_default_progress,
        test_custom_progress_callback,
        test_progress_with_different_limits,
        test_progress_without_callback,
        test_progress_with_date_filter
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
            await asyncio.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n\nSummary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All progress tracking tests passed!")
        print("\nProgress tracking is working correctly. You can use:")
        print("  - with_progress=True for default progress display")
        print("  - Custom progress_callback for your own progress handling")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)