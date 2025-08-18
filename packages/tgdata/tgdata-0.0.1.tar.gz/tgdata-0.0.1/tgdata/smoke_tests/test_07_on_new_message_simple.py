"""
Simple test for real-time message events using on_new_message decorator
"""
# To run: python -m tgdata.smoke_tests.test_07_on_new_message_simple

import asyncio
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import signal

# Global to track received messages
received_messages = []

async def test_on_new_message():
    """Test real-time message reception with on_new_message decorator"""
    print("Real-time Message Event Test")
    print("=" * 50)
    
    try:
        # Initialize TgData
        tg = TgData("config.ini")
        
        # Test group
        test_group_id = 4611400320  # BudgetyAIDev
        print(f"Monitoring group ID: {test_group_id}")
        
        # Register event handler for new messages
        @tg.on_new_message(group_id=test_group_id)
        async def handle_new_message(event):
            """Handler for new messages in the test group"""
            message_text = event.message.text or "[No text]"
            sender_id = event.sender_id
            message_id = event.message.id
            
            # Track the message
            received_messages.append({
                'id': message_id,
                'text': message_text,
                'sender': sender_id,
                'time': datetime.now()
            })
            
            print(f"\n📨 New message received!")
            print(f"   ID: {message_id}")
            print(f"   From: {sender_id}")
            print(f"   Text: {message_text[:100]}")
            print(f"   Total received: {len(received_messages)}")
        
        print("\n✓ Event handler queued")
        print("\nInstructions:")
        print("1. Send test messages to the group")
        print("2. Messages should appear in real-time")
        print("3. Press Ctrl+C to stop monitoring")
        print("\nWaiting for messages...")
        print("-" * 50)
        
        # Run the event loop (this will register handlers and start listening)
        await tg.run_with_event_loop()
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("Test stopped by user")
        print(f"Total messages received: {len(received_messages)}")
        
        if received_messages:
            print("\nReceived message IDs:")
            for msg in received_messages:
                print(f"  - {msg['id']}: {msg['text'][:30]}...")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_on_new_message_with_timeout():
    """Test real-time messages with automatic timeout"""
    print("\nReal-time Message Test (30 second timeout)")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        test_group_id = 4611400320
        
        message_count = 0
        start_time = datetime.now()
        
        # Get the client first
        client = await tg.connection_engine.get_client()
        
        # Import events from telethon
        from telethon import events
        
        # Register handler directly on the client
        @client.on(events.NewMessage(chats=test_group_id))
        async def count_messages(event):
            nonlocal message_count
            message_count += 1
            elapsed = (datetime.now() - start_time).seconds
            message_text = event.message.text or "[No text]"
            print(f"[{elapsed}s] Message #{message_count}: {message_text[:50]}")
        
        print(f"Monitoring group {test_group_id} for 30 seconds...")
        print("Send messages now!")
        print("-" * 50)
        
        # Give time for handler to register
        await asyncio.sleep(0.5)
        
        try:
            # Run with timeout
            await asyncio.wait_for(
                client.run_until_disconnected(),
                timeout=30
            )
        except asyncio.TimeoutError:
            print("-" * 50)
            print(f"✓ Test completed - received {message_count} messages in 30 seconds")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run real-time message tests"""
    print("Choose test mode:")
    print("1. Continuous monitoring (Ctrl+C to stop)")
    print("2. 30-second timeout test")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        await test_on_new_message_with_timeout()
    else:
        await test_on_new_message()
    
    print("\n✓ Test completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✓ Test stopped by user")
        sys.exit(0)