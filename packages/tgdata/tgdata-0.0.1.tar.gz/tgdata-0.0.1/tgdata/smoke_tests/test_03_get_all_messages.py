"""
Test: Get All Messages
Demonstrates extracting ALL messages from a group and saving to CSV
"""

# python -m tgdata.smoke_tests.test_get_all_messages

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData


async def test_get_all_messages():
    """Get all messages from a group and save to CSV"""
    
    # Configuration
    group_id = int(os.environ.get('TEST_GROUP_ID', '1670178185'))  # Bitcoinsensus by default
    output_csv = 'all_messages.csv'
    
    print(f"Getting ALL messages from group {group_id}")
    print(f"Output file: {output_csv}")
    print("-" * 50)
    
    try:
        # Initialize TgData
        tg = TgData("config.ini")
        
        # Get ALL messages (after_id=0 means start from beginning)
        print("\nExtracting messages...")
        
        all_messages = await tg.get_messages(
            group_id=group_id,
            after_id=0  # Start from the beginning
        )
        
        if not all_messages.empty:
            # Save to CSV
            all_messages.to_csv(output_csv, index=False)
            print(f"\n✅ Saved {len(all_messages)} messages to {output_csv}")
            return True
        else:
            print("No messages found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await tg.close()


async def main():
    """Run the test"""
    print("Test: Get All Messages")
    print("-" * 30)
    
    success = await test_get_all_messages()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())