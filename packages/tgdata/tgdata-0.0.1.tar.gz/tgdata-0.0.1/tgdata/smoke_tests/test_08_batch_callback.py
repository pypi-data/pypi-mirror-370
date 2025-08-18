"""
Smoke test for batch callback functionality
"""
# To run: python -m tgdata.smoke_tests.test_08_batch_callback

import asyncio
import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import pandas as pd


async def test_batch_callback_basic():
    """Test basic batch callback functionality"""
    print("TEST: Basic batch callback functionality")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        # Get groups
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available for testing")
            return False
            
        # Select a group with enough messages
        test_group = None
        for _, group in groups.iterrows():
            if group['ParticipantsCount'] and group['ParticipantsCount'] > 10:
                test_group = group
                break
        
        if test_group is None:
            test_group = groups.iloc[0]
            
        print(f"Using group: {test_group['Title']} (ID: {test_group['GroupID']})")
        
        # Track batches
        batches_received = []
        
        async def batch_handler(batch_df, batch_info):
            """Process each batch as it arrives"""
            batches_received.append({
                'batch_num': batch_info['batch_num'],
                'size': len(batch_df),
                'total_so_far': batch_info['total_processed']
            })
            
            print(f"\n  Batch #{batch_info['batch_num']}:")
            print(f"    - Messages in batch: {len(batch_df)}")
            print(f"    - Total processed: {batch_info['total_processed']}")
            if 'is_final' in batch_info:
                print(f"    - This is the final batch")
            
            # Show sample message from batch
            if not batch_df.empty:
                first_msg = batch_df.iloc[0]
                msg_text = first_msg.get('Message', 'No text')[:50]
                print(f"    - First message: {msg_text}...")
        
        print("\nFetching messages in batches of 50...")
        print("-" * 50)
        
        # Fetch with batch callback
        messages = await tg.get_messages(
            group_id=int(test_group['GroupID']),
            limit=200,
            batch_size=50,
            batch_callback=batch_handler
        )
        
        print(f"\n✓ Total messages fetched: {len(messages)}")
        print(f"✓ Number of batches: {len(batches_received)}")
        
        # Verify batches
        if batches_received:
            print("\nBatch summary:")
            for batch in batches_received:
                print(f"  Batch {batch['batch_num']}: {batch['size']} messages")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Batch callback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_callback_with_etl():
    """Test batch callback for ETL-style processing"""
    print("\n\nTEST: Batch callback for ETL processing")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
            
        test_group = groups.iloc[0]
        print(f"Using group: {test_group['Title']}")
        
        # Simulate ETL processing
        etl_stats = {
            'batches_processed': 0,
            'messages_transformed': 0,
            'messages_loaded': 0,
            'processing_times': []
        }
        
        async def etl_batch_processor(batch_df, batch_info):
            """ETL processing for each batch"""
            start_time = time.time()
            
            # Extract phase (already done by get_messages)
            print(f"\n[ETL] Processing batch {batch_info['batch_num']} ({len(batch_df)} messages)")
            
            # Transform phase
            print("  → Transforming data...")
            # Add computed fields
            batch_df['word_count'] = batch_df['Message'].fillna('').str.split().str.len()
            batch_df['has_links'] = batch_df['Message'].fillna('').str.contains('http', case=False)
            batch_df['extracted_at'] = datetime.now()
            batch_df['batch_id'] = batch_info['batch_num']
            
            etl_stats['messages_transformed'] += len(batch_df)
            
            # Load phase (simulated)
            print("  → Loading to destination...")
            # In real ETL, this would be:
            # await load_to_database(batch_df)
            # await send_to_kafka(batch_df)
            await asyncio.sleep(0.1)  # Simulate load time
            
            etl_stats['messages_loaded'] += len(batch_df)
            etl_stats['batches_processed'] += 1
            
            # Track performance
            process_time = time.time() - start_time
            etl_stats['processing_times'].append(process_time)
            
            print(f"  ✓ Batch {batch_info['batch_num']} complete in {process_time:.2f}s")
        
        print("\nRunning ETL pipeline with batch size of 25...")
        print("-" * 50)
        
        messages = await tg.get_messages(
            group_id=int(test_group['GroupID']),
            limit=100,
            batch_size=25,
            batch_callback=etl_batch_processor
        )
        
        # Show ETL summary
        print(f"\n{'='*50}")
        print("ETL Pipeline Summary:")
        print(f"  Total messages: {len(messages)}")
        print(f"  Batches processed: {etl_stats['batches_processed']}")
        print(f"  Messages transformed: {etl_stats['messages_transformed']}")
        print(f"  Messages loaded: {etl_stats['messages_loaded']}")
        
        if etl_stats['processing_times']:
            avg_time = sum(etl_stats['processing_times']) / len(etl_stats['processing_times'])
            print(f"  Average batch processing time: {avg_time:.2f}s")
        
        print("\n✓ ETL batch processing completed successfully")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ ETL batch test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_callback_with_progress():
    """Test batch callback combined with progress tracking"""
    print("\n\nTEST: Batch callback with progress tracking")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
            
        test_group = groups.iloc[0]
        print(f"Using group: {test_group['Title']}")
        
        # Track both progress and batches
        batch_count = 0
        
        async def batch_callback(batch_df, batch_info):
            nonlocal batch_count
            batch_count += 1
            # Simple batch notification
            print(f"\n  [Batch {batch_count}] Received {len(batch_df)} messages")
        
        def progress_callback(current, total, rate):
            # Progress bar
            if total:
                bar_length = 30
                filled = int(bar_length * current / total)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  Progress: [{bar}] {current}/{total} @ {rate:.1f} msg/s", end="")
        
        print("\nFetching with both progress and batch callbacks...")
        print("-" * 50)
        
        messages = await tg.get_messages(
            group_id=int(test_group['GroupID']),
            limit=150,
            batch_size=50,
            batch_callback=batch_callback,
            with_progress=True,
            progress_callback=progress_callback
        )
        
        print(f"\n\n✓ Fetched {len(messages)} messages in {batch_count} batches")
        print("✓ Both progress tracking and batch processing worked together")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Combined callback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_callback_error_handling():
    """Test batch callback error handling"""
    print("\n\nTEST: Batch callback error handling")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
            
        test_group = groups.iloc[0]
        print(f"Using group: {test_group['Title']}")
        
        successful_batches = []
        
        async def failing_batch_callback(batch_df, batch_info):
            """Callback that sometimes fails"""
            batch_num = batch_info['batch_num']
            
            # Simulate error on batch 2
            if batch_num == 2:
                print(f"\n  [Batch {batch_num}] Simulating processing error...")
                raise ValueError("Simulated batch processing error")
            
            successful_batches.append(batch_num)
            print(f"\n  [Batch {batch_num}] Processed successfully")
        
        print("\nTesting batch callback with simulated errors...")
        print("-" * 50)
        
        try:
            messages = await tg.get_messages(
                group_id=int(test_group['GroupID']),
                limit=100,
                batch_size=30,
                batch_callback=failing_batch_callback
            )
            print(f"\n✗ Should have raised an error")
            await tg.close()
            return False
        except ValueError as e:
            print(f"\n✓ Correctly caught batch processing error: {e}")
            print(f"✓ Successfully processed batches before error: {successful_batches}")
            await tg.close()
            return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all batch callback tests"""
    print("Batch Callback Feature Tests")
    print("=" * 70)
    print("\nThese tests demonstrate batch processing callbacks for ETL workflows.\n")
    
    tests = [
        test_batch_callback_basic,
        test_batch_callback_with_etl,
        test_batch_callback_with_progress,
        test_batch_callback_error_handling
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
        print("\n✓ All batch callback tests passed!")
        print("\nBatch callbacks enable:")
        print("  - Process messages in chunks during fetching")
        print("  - Memory-efficient ETL pipelines")
        print("  - Stream-style processing for large datasets")
        print("  - Combine with progress tracking for full visibility")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    print("Starting batch callback tests...")
    print("Note: These tests demonstrate ETL-style batch processing\n")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)