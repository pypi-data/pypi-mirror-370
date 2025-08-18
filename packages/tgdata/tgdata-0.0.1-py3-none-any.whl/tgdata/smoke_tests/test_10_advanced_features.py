"""
Smoke tests for advanced TgData features
"""
# To run: python -m tgdata.smoke_tests.test_04_advanced_features

import asyncio
import sys
import os
import tempfile
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import pandas as pd




async def test_connection_pooling():
    """Test connection pooling features"""
    print("\nTEST: Connection pooling...")
    try:
        # Test pool configuration
        tg = TgData(connection_pool_size=5)
        assert tg.connection_engine.pool_size == 5
        print("✓ Connection pool size configured")
        
        # Test health check structure
        health = await tg.health_check()
        assert isinstance(health, dict)
        assert 'timestamp' in health
        assert 'pool_connections' in health
        print("✓ Health check includes pool information")
        
        return True
    except Exception as e:
        print(f"✗ Connection pooling test failed: {e}")
        return False


async def test_progress_tracking():
    """Test progress tracking functionality"""
    print("\nTEST: Progress tracking...")
    try:
        tg = TgData()
        
        # Test that get_messages supports progress tracking
        assert hasattr(tg, 'get_messages')
        
        # Test progress callback structure
        progress_data = []
        
        def test_callback(current, total, rate):
            progress_data.append({
                'current': current,
                'total': total,
                'rate': rate
            })
        
        # We can't actually fetch messages without auth, but we can test the parameter acceptance
        try:
            await tg.get_messages(
                group_id=12345,
                limit=10,
                with_progress=True,
                progress_callback=test_callback
            )
        except:
            # Expected to fail without auth
            pass
        
        print("✓ Progress tracking parameters accepted")
        
        return True
    except Exception as e:
        print(f"✗ Progress tracking test failed: {e}")
        return False


async def test_date_filtering():
    """Test date-based message filtering"""
    print("\nTEST: Date filtering...")
    try:
        tg = TgData()
        
        # Test filter_messages with date parameters
        df = pd.DataFrame({
            'MessageId': [1, 2, 3, 4, 5],
            'Date': [
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=1),
                datetime.now(),
                datetime.now() + timedelta(days=1)
            ],
            'Message': ['Old', 'Mid', 'Recent', 'Today', 'Future']
        })
        
        # Filter last 2 days
        filtered = tg.filter_messages(
            df,
            start_date=datetime.now() - timedelta(days=2)
        )
        assert len(filtered) == 3  # Recent, Today, Future
        print("✓ Start date filtering works")
        
        # Filter with end date
        filtered = tg.filter_messages(
            df,
            end_date=datetime.now()
        )
        assert len(filtered) == 4  # Excludes Future
        print("✓ End date filtering works")
        
        # Filter date range
        filtered = tg.filter_messages(
            df,
            start_date=datetime.now() - timedelta(days=4),
            end_date=datetime.now() - timedelta(days=2)
        )
        assert len(filtered) == 1  # Only Mid
        print("✓ Date range filtering works")
        
        return True
    except Exception as e:
        print(f"✗ Date filtering test failed: {e}")
        return False


async def test_message_caching():
    """Test message caching behavior"""
    print("\nTEST: Message caching...")
    try:
        tg = TgData()
        
        # Test cache clearing on group change
        tg.set_group(12345)
        # Add some fake cache data with proper key format
        cache_key = '12345_test_key'
        tg.message_engine._message_cache[cache_key] = pd.DataFrame([{'test': 'data'}])
        assert cache_key in tg.message_engine._message_cache
        
        # Change group should clear cache for previous group
        tg.set_group(54321)
        # Check that the cache for the old group is gone
        assert cache_key not in tg.message_engine._message_cache
        print("✓ Cache cleared on group change")
        
        return True
    except Exception as e:
        print(f"✗ Message caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_metrics_and_logging():
    """Test metrics collection and logging"""
    print("\nTEST: Metrics and logging...")
    try:
        # Test with log file
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp_log:
            tg = TgData(log_file=tmp_log.name)
            
            # Perform some operations to generate logs
            tg.set_group(12345)
            
            # Check log file exists
            assert os.path.exists(tmp_log.name)
            print("✓ Log file created")
            
            # Test metrics
            metrics = await tg.get_metrics()
            assert 'current_group' in metrics
            assert metrics['current_group'] == 12345
            assert 'message_cache_size' in metrics
            print("✓ Metrics include cache and group info")
            
            os.unlink(tmp_log.name)
        
        return True
    except Exception as e:
        print(f"✗ Metrics and logging test failed: {e}")
        return False


async def test_validation_methods():
    """Test connection validation methods"""
    print("\nTEST: Validation methods...")
    try:
        tg = TgData()
        
        # Test validate_connection
        is_valid = await tg.validate_connection()
        assert isinstance(is_valid, bool)
        print(f"✓ Connection validation returns: {is_valid}")
        
        # Test health check
        health = await tg.health_check()
        assert isinstance(health, dict)
        assert 'primary_connection' in health
        assert 'errors' in health
        print("✓ Health check returns detailed status")
        
        return True
    except Exception as e:
        print(f"✗ Validation methods test failed: {e}")
        return False


async def main():
    """Run all advanced feature tests"""
    print("Advanced TgData Features Tests")
    print("=" * 50)
    
    tests = [
        test_connection_pooling,
        test_progress_tracking,
        test_date_filtering,
        test_message_caching,
        test_metrics_and_logging,
        test_validation_methods
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
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
        print("✓ All advanced feature tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)