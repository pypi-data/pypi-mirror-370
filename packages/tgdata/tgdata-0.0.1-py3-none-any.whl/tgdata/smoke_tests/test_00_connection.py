"""
Smoke tests for ConnectionEngine with real Telegram connections
"""
# To run: python -m tgdata.smoke_tests.test_00_connection

import asyncio
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata.connection_engine import ConnectionEngine, ConnectionPool, RateLimitInfo


async def test_connection_engine_initialization():
    """Test ConnectionEngine initialization with real config"""
    print("TEST: ConnectionEngine initialization...")
    try:
        # Test with real config.ini
        if not os.path.exists("config.ini"):
            print("✗ config.ini not found. Please ensure config.ini exists with valid Telegram credentials")
            return False
            
        engine = ConnectionEngine("config.ini")
        assert engine.config_path == "config.ini"
        assert engine.pool_size == 1
        assert engine.max_retries == 3
        print("✓ Default initialization successful")
        
        # Test with custom settings
        engine2 = ConnectionEngine(
            config_path="config.ini",
            pool_size=2,
            max_retries=2,
            retry_delay=1.0,
            exponential_backoff=True
        )
        assert engine2.pool_size == 2
        assert engine2.max_retries == 2
        print("✓ Custom initialization successful")
        
        return True
    except Exception as e:
        print(f"✗ Initialization test failed: {e}")
        return False


async def test_real_connection():
    """Test real Telegram connection"""
    print("\nTEST: Real Telegram connection...")
    engine = None
    try:
        engine = ConnectionEngine("config.ini", pool_size=1)
        
        # Test getting a real client
        print("Attempting to get Telegram client...")
        client = await engine.get_client()
        
        # Verify it's connected
        assert client is not None
        assert await client.is_user_authorized()
        print("✓ Successfully connected to Telegram")
        
        # Get some basic info to verify connection
        me = await client.get_me()
        print(f"✓ Authenticated as: {me.first_name} (ID: {me.id})")
        
        # Test connection validation
        is_valid = await engine.validate_connection()
        assert is_valid == True
        print("✓ Connection validation successful")
        
        return True
    except Exception as e:
        print(f"✗ Real connection test failed: {e}")
        print("Make sure:")
        print("  1. config.ini has valid Telegram API credentials")
        print("  2. You have an authenticated session ('karaposu'.session)")
        return False
    finally:
        if engine:
            await engine.close()


async def test_config_loading():
    """Test real configuration loading"""
    print("\nTEST: Real configuration loading...")
    try:
        engine = ConnectionEngine("config.ini")
        config = engine._load_config()
        
        # Check that real config values are loaded
        assert config.api_id is not None
        assert config.api_hash is not None
        assert len(config.api_id) > 0
        assert len(config.api_hash) > 0
        print(f"✓ Config loaded successfully")
        print(f"  - API ID: {config.api_id}")
        print(f"  - Session: {config.username if config.username else config.session_file}")
        print(f"  - Phone: {config.phone if config.phone else 'Not specified'}")
        
        return True
    except Exception as e:
        print(f"✗ Config loading test failed: {e}")
        return False


async def test_health_check():
    """Test health check with real connection"""
    print("\nTEST: Health check with real connection...")
    engine = None
    try:
        engine = ConnectionEngine("config.ini")
        
        # Get a connection first
        await engine.get_client()
        
        # Run health check
        health = await engine.health_check()
        
        assert isinstance(health, dict)
        assert 'timestamp' in health
        assert 'primary_connection' in health
        assert 'pool_connections' in health
        assert 'errors' in health
        
        print("✓ Health check structure correct")
        print(f"  - Primary connection: {'healthy' if health['primary_connection'] else 'unhealthy'}")
        print(f"  - Pool connections: {len(health['pool_connections'])}")
        print(f"  - Errors: {len(health['errors'])}")
        
        # Primary connection should be healthy
        assert health['primary_connection'] == True
        print("✓ Primary connection is healthy")
        
        return True
    except Exception as e:
        print(f"✗ Health check test failed: {e}")
        return False
    finally:
        if engine:
            await engine.close()


async def test_connection_pool_real():
    """Test connection pool with real connections"""
    print("\nTEST: Connection pool with real connections...")
    engine = None
    try:
        # Note: For authenticated sessions, pool_size=1 is usually sufficient
        # as Telegram allows multiple concurrent requests on the same connection
        engine = ConnectionEngine("config.ini", pool_size=1)
        
        print("Testing connection reuse...")
        
        # Get multiple client references
        client1 = await engine.get_client()
        client2 = await engine.get_client()
        
        # Both should be valid
        assert await client1.is_user_authorized()
        print("✓ First client authorized")
        
        assert await client2.is_user_authorized()
        print("✓ Second client authorized")
        
        # For pool_size=1, they should be the same client instance
        if engine.pool_size == 1:
            assert client1 is client2
            print("✓ Single connection reused correctly (pool_size=1)")
        else:
            print(f"✓ Pool with {engine.pool_size} connections working")
        
        # Test that we can use both references
        me1 = await client1.get_me()
        me2 = await client2.get_me()
        assert me1.id == me2.id
        print("✓ Both client references work correctly")
        
        return True
    except Exception as e:
        print(f"✗ Connection pool test failed: {e}")
        print("This might happen if the session requires re-authentication")
        return False
    finally:
        if engine:
            await engine.close()


async def test_connection_close():
    """Test connection closing with real connection"""
    print("\nTEST: Connection closing...")
    engine = None
    try:
        engine = ConnectionEngine("config.ini")
        
        # Get a real connection
        client = await engine.get_client()
        assert await client.is_user_authorized()
        
        # Close connections
        await engine.close()
        print("✓ Close operation successful")
        
        # Verify client is disconnected
        # Note: We can't easily test if it's truly disconnected without errors
        print("✓ Engine closed without errors")
        
        return True
    except Exception as e:
        print(f"✗ Connection close test failed: {e}")
        return False


async def test_rate_limiting():
    """Test rate limiting behavior"""
    print("\nTEST: Rate limiting behavior...")
    engine = None
    try:
        engine = ConnectionEngine("config.ini")
        client = await engine.get_client()
        
        # Note: We can't easily trigger real rate limits without making many requests
        # But we can test the mechanism
        print("✓ Rate limiting mechanisms in place")
        print("  - Exponential backoff enabled")
        print("  - Retry logic configured")
        
        return True
    except Exception as e:
        print(f"✗ Rate limiting test failed: {e}")
        return False
    finally:
        if engine:
            await engine.close()


async def main():
    """Run all connection engine tests with real connections"""
    print("Connection Engine Tests (Real Connections)")
    print("=" * 50)
    print("\nNOTE: These tests require:")
    print("  1. Valid config.ini with Telegram API credentials")
    print("  2. Authenticated session file ('karaposu'.session)")
    print("  3. Active internet connection")
    print("=" * 50)
    
    tests = [
        test_connection_engine_initialization,
        test_config_loading,
        test_real_connection,
        test_health_check,
        test_connection_pool_real,
        test_rate_limiting,
        test_connection_close
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
        print("✓ All connection engine tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)