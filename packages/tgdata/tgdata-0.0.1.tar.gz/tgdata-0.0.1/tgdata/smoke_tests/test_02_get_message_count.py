"""
Test: Get Message Count
Demonstrates getting total message count without fetching all messages
"""

# to run python -m tgdata.smoke_tests.test_02_get_message_count

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData


async def test_get_message_count():
    """Get message count for a group"""
    
    # Configuration
    group_id = int(os.environ.get('TEST_GROUP_ID', '1670178185'))  # Bitcoinsensus by default
    
    print(f"Getting message count for group {group_id}")
    print("-" * 40)
    
    try:
        # Initialize TgData
        tg = TgData("config.ini")
        
        # Get message count
        print("\nFetching count...")
        count = await tg.get_message_count(group_id=group_id)
        
        print(f"\n✅ Total messages in group: {count:,}")
        
        # Also test with multiple groups if available
        print("\nChecking all accessible groups...")
        groups = await tg.list_groups()
        
        if not groups.empty:
            print(f"\nMessage counts for all groups:")
            print("-" * 40)
            
            for _, group in groups.head(5).iterrows():  # Limit to first 5 groups
                try:
                    count = await tg.get_message_count(group_id=group['GroupID'])
                    print(f"{group['Title'][:30]:30} : {count:,} messages")
                except Exception as e:
                    print(f"{group['Title'][:30]:30} : Error - {str(e)[:20]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await tg.close()


async def main():
    """Run the test"""
    print("Test: Get Message Count")
    print("=" * 40)
    
    success = await test_get_message_count()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())