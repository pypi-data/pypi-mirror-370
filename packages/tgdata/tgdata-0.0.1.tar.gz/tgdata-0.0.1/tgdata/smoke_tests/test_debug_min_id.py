"""
Debug test to understand Telethon's min_id behavior
"""


# python -m tgdata.smoke_tests.test_debug_min_id
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_min_id_behavior():
    """Test how Telethon's iter_messages handles min_id"""
    print("Testing Telethon min_id behavior")
    print("=" * 50)
    
    # Use TgData to get the client (handles session properly)
    tg = TgData("config.ini")
    client = await tg.connection_engine.get_client()
    
    group_id = 4611400320  # BudgetyAIDev test group
    
    try:
        # Test 1: Get last 5 messages normally
        print("\n1. Getting last 5 messages (normal order):")
        messages = []
        async for msg in client.iter_messages(group_id, limit=5):
            if msg.text:
                messages.append((msg.id, msg.text[:20]))
        
        for msg_id, text in messages:
            print(f"   ID {msg_id}: {text}")
        
        # Test 2: Get messages with min_id
        if messages:
            test_min_id = messages[2][0]  # Middle message ID
            print(f"\n2. Getting messages with min_id={test_min_id}:")
            
            found_messages = []
            async for msg in client.iter_messages(group_id, min_id=test_min_id, limit=5):
                if msg.text:
                    found_messages.append((msg.id, msg.text[:20]))
            
            for msg_id, text in found_messages:
                print(f"   ID {msg_id}: {text}")
            
            # Test 3: Same but with reverse=True
            print(f"\n3. Getting messages with min_id={test_min_id} and reverse=True:")
            found_messages = []
            async for msg in client.iter_messages(group_id, min_id=test_min_id, reverse=True, limit=5):
                if msg.text:
                    found_messages.append((msg.id, msg.text[:20]))
            
            for msg_id, text in found_messages:
                print(f"   ID {msg_id}: {text}")
                
            # Test 4: Using offset_id instead
            print(f"\n4. Getting messages with offset_id={test_min_id}:")
            found_messages = []
            async for msg in client.iter_messages(group_id, offset_id=test_min_id, limit=5):
                if msg.text:
                    found_messages.append((msg.id, msg.text[:20]))
            
            for msg_id, text in found_messages:
                print(f"   ID {msg_id}: {text}")
                
            # Test 5: What about add_offset?
            print(f"\n5. Getting messages with offset_id={test_min_id} and add_offset=-1:")
            found_messages = []
            async for msg in client.iter_messages(group_id, offset_id=test_min_id, add_offset=-1, limit=5):
                if msg.text:
                    found_messages.append((msg.id, msg.text[:20]))
            
            for msg_id, text in found_messages:
                print(f"   ID {msg_id}: {text}")
        
    finally:
        await tg.close()
    
    print("\n" + "=" * 50)
    print("Analysis complete!")


if __name__ == "__main__":
    asyncio.run(test_min_id_behavior())