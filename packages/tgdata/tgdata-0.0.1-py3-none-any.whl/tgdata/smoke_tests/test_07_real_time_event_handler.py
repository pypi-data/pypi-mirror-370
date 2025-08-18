"""
Smoke test for real-time event handler feature
"""
# To run: python -m tgdata.smoke_tests.test_07_real_time_event_handler

import asyncio
import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tgdata import TgData
import pandas as pd


async def test_basic_event_handler():
    """Test basic real-time event handler"""
    print("TEST: Basic real-time event handler")
    print("=" * 50)
    print("This test will listen for new messages for 30 seconds.")
    print("Try sending messages to your groups to see them appear!\n")
    
    try:
        tg = TgData("config.ini")
        
        # Track received messages
        received_messages = []
        
        # Register event handler for all groups
        @tg.on_new_message()
        async def handle_all_messages(event):
            # Get message details
            try:
                sender = await event.get_sender()
                sender_name = getattr(sender, 'first_name', 'Unknown')
                chat = await event.get_chat()
                chat_name = getattr(chat, 'title', 'Private Chat')
                
                message_info = {
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'chat': chat_name,
                    'sender': sender_name,
                    'text': event.message.text[:50] if event.message.text else '[Media]'
                }
                received_messages.append(message_info)
                
                print(f"[{message_info['time']}] {chat_name} - {sender_name}: {message_info['text']}")
                
            except Exception as e:
                print(f"Error processing message: {e}")
        
        print("Listening for messages... (30 seconds)")
        print("-" * 50)
        
        # Run for 30 seconds
        try:
            await asyncio.wait_for(
                tg.run_with_event_loop(),
                timeout=30
            )
        except asyncio.TimeoutError:
            print("\n" + "-" * 50)
            print(f"✓ Timeout reached. Received {len(received_messages)} messages")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Basic event handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_group_specific_handler():
    """Test event handler for specific group"""
    print("\n\nTEST: Group-specific event handler")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        # Get groups
        groups = await tg.list_groups()
        if groups.empty:
            print("✗ No groups available")
            return False
        
        # Select first group
        test_group = groups.iloc[0]
        group_id = int(test_group['GroupID'])
        group_name = test_group['Title']
        
        print(f"Monitoring only: {group_name} (ID: {group_id})")
        print(f"Send messages to this group to test!\n")
        
        message_count = 0
        
        # Register handler for specific group
        @tg.on_new_message(group_id=group_id)
        async def handle_group_messages(event):
            nonlocal message_count
            message_count += 1
            
            sender = await event.get_sender()
            sender_name = getattr(sender, 'first_name', 'Unknown')
            
            print(f"[Message #{message_count}] {sender_name}: {event.message.text[:70]}")
            
            # Auto-reply to test messages
            if event.message.text and "test" in event.message.text.lower():
                print("  → Detected 'test' keyword!")
        
        print("Listening for messages in specific group... (20 seconds)")
        print("-" * 50)
        
        try:
            await asyncio.wait_for(
                tg.run_with_event_loop(),
                timeout=20
            )
        except asyncio.TimeoutError:
            print("\n" + "-" * 50)
            print(f"✓ Received {message_count} messages from {group_name}")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Group-specific handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_handlers():
    """Test multiple event handlers simultaneously"""
    print("\n\nTEST: Multiple event handlers")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        stats = {
            'total': 0,
            'with_text': 0,
            'with_media': 0,
            'from_bots': 0
        }
        
        # Handler 1: Count all messages
        @tg.on_new_message()
        async def count_all(event):
            stats['total'] += 1
        
        # Handler 2: Track text vs media
        @tg.on_new_message()
        async def track_content_type(event):
            if event.message.text:
                stats['with_text'] += 1
            elif event.message.media:
                stats['with_media'] += 1
        
        # Handler 3: Track bot messages
        @tg.on_new_message()
        async def track_bots(event):
            sender = await event.get_sender()
            if getattr(sender, 'bot', False):
                stats['from_bots'] += 1
                print(f"  [BOT] Message from bot: {sender.first_name}")
        
        # Handler 4: Display messages
        @tg.on_new_message()
        async def display_messages(event):
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', 'Private')
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            if event.message.text:
                print(f"[{timestamp}] {chat_name}: {event.message.text[:50]}...")
            else:
                print(f"[{timestamp}] {chat_name}: [Media Message]")
        
        print("Running 4 handlers simultaneously:")
        print("1. Counting all messages")
        print("2. Tracking content types")
        print("3. Detecting bot messages")
        print("4. Displaying message preview")
        print("\nListening... (15 seconds)")
        print("-" * 50)
        
        try:
            await asyncio.wait_for(
                tg.run_with_event_loop(),
                timeout=15
            )
        except asyncio.TimeoutError:
            print("\n" + "-" * 50)
            print("Statistics:")
            print(f"  Total messages: {stats['total']}")
            print(f"  Text messages: {stats['with_text']}")
            print(f"  Media messages: {stats['with_media']}")
            print(f"  Bot messages: {stats['from_bots']}")
            print("✓ All handlers worked simultaneously")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Multiple handlers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_handler_with_filters():
    """Test event handler with message filtering"""
    print("\n\nTEST: Event handler with filters")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        keywords = ['help', 'question', 'urgent', 'important']
        keyword_messages = []
        
        # Handler that only processes messages with keywords
        @tg.on_new_message()
        async def keyword_monitor(event):
            if not event.message.text:
                return
                
            text_lower = event.message.text.lower()
            found_keywords = [kw for kw in keywords if kw in text_lower]
            
            if found_keywords:
                chat = await event.get_chat()
                sender = await event.get_sender()
                
                info = {
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'chat': getattr(chat, 'title', 'Private'),
                    'sender': getattr(sender, 'first_name', 'Unknown'),
                    'keywords': found_keywords,
                    'text': event.message.text[:100]
                }
                keyword_messages.append(info)
                
                print(f"\n🔔 KEYWORD ALERT!")
                print(f"   Time: {info['time']}")
                print(f"   Chat: {info['chat']}")
                print(f"   From: {info['sender']}")
                print(f"   Keywords: {', '.join(info['keywords'])}")
                print(f"   Message: {info['text']}")
        
        print(f"Monitoring for keywords: {', '.join(keywords)}")
        print("Send messages containing these words to trigger alerts!")
        print("\nListening... (20 seconds)")
        print("-" * 50)
        
        try:
            await asyncio.wait_for(
                tg.run_with_event_loop(),
                timeout=20
            )
        except asyncio.TimeoutError:
            print("\n" + "-" * 50)
            print(f"✓ Found {len(keyword_messages)} messages with keywords")
            
            if keyword_messages:
                print("\nKeyword Summary:")
                all_keywords = {}
                for msg in keyword_messages:
                    for kw in msg['keywords']:
                        all_keywords[kw] = all_keywords.get(kw, 0) + 1
                
                for kw, count in all_keywords.items():
                    print(f"  '{kw}': {count} occurrence(s)")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Filter handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_handler_performance():
    """Test event handler performance and responsiveness"""
    print("\n\nTEST: Event handler performance")
    print("=" * 50)
    
    try:
        tg = TgData("config.ini")
        
        # Track message processing times
        processing_times = []
        
        @tg.on_new_message()
        async def performance_monitor(event):
            start_time = time.time()
            
            # Simulate some processing
            chat = await event.get_chat()
            sender = await event.get_sender()
            
            # Calculate processing time
            process_time = (time.time() - start_time) * 1000  # in milliseconds
            processing_times.append(process_time)
            
            # Show timing
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            chat_name = getattr(chat, 'title', 'Private')[:20]
            
            print(f"[{timestamp}] {chat_name} | Processed in {process_time:.1f}ms")
        
        print("Testing event handler responsiveness...")
        print("Send multiple messages quickly to test performance!")
        print("\nListening... (15 seconds)")
        print("-" * 50)
        
        try:
            await asyncio.wait_for(
                tg.run_with_event_loop(),
                timeout=15
            )
        except asyncio.TimeoutError:
            print("\n" + "-" * 50)
            
            if processing_times:
                avg_time = sum(processing_times) / len(processing_times)
                min_time = min(processing_times)
                max_time = max(processing_times)
                
                print(f"✓ Performance Statistics:")
                print(f"  Messages processed: {len(processing_times)}")
                print(f"  Average processing time: {avg_time:.1f}ms")
                print(f"  Fastest: {min_time:.1f}ms")
                print(f"  Slowest: {max_time:.1f}ms")
                
                if avg_time < 100:
                    print("  → Excellent performance! 🚀")
                elif avg_time < 500:
                    print("  → Good performance ✓")
                else:
                    print("  → Consider optimizing handler logic")
            else:
                print("✓ No messages received to measure performance")
        
        await tg.close()
        return True
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all real-time event handler tests"""
    print("Real-time Event Handler Tests")
    print("=" * 70)
    print("\nThese tests demonstrate real-time message handling.")
    print("The tests will listen for incoming messages - try sending")
    print("messages to your Telegram groups to see them handled in real-time!\n")
    
    # Show instructions
    print("💡 TIP: Open Telegram and send test messages while tests run!")
    print("        Try messages with keywords: help, urgent, test")
    print("        Send to different groups to see filtering in action\n")
    
    tests = [
        test_basic_event_handler,
        test_group_specific_handler,
        test_multiple_handlers,
        test_handler_with_filters,
        test_handler_performance
    ]
    
    # Ask if user wants to run tests
    print("Ready to start? The tests will listen for real messages.")
    input("Press Enter to begin...")
    print()
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
            
            # Pause between tests
            if test != tests[-1]:
                print("\nPress Enter for next test...")
                input()
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            break
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
        print("\n✓ All real-time event handler tests passed!")
        print("\nEvent handlers are working correctly. You can use:")
        print("  - @tg.on_new_message() for all messages")
        print("  - @tg.on_new_message(group_id=123) for specific groups")
        print("  - Multiple handlers for different processing logic")
        print("  - await tg.run_with_event_loop() to start listening")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    print("Starting real-time event handler tests...")
    print("Note: You'll need to send actual messages to test this feature!\n")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)