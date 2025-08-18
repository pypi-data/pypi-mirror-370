# tgdata

A production-grade Python library for extracting and processing Telegram group and channel messages. Designed for ETL pipelines, data analysis, and archival purposes.

## Features

- 🚀 **Production-Ready**: Built for reliability and scale in ETL pipelines
- 📊 **Efficient Data Extraction**: Fetch messages from groups and channels with rate limit handling
- 🔄 **Incremental Updates**: Fetch only new messages with `after_id` parameter
- 📈 **Progress Tracking**: Monitor long-running operations with real-time progress
- 🔌 **Clean Architecture**: Focused on data extraction with minimal dependencies
- 🛡️ **Robust Error Handling**: Automatic retries with exponential backoff
- 📁 **Multiple Export Formats**: Export to CSV, JSON, or integrate with your data pipeline
- 🔔 **Real-time Updates**: Listen for new messages with event handlers
- ⏱️ **Polling Support**: Poll for new messages at configurable intervals

## Installation

```bash
pip install tgdata
```


## Authentication

tgdata supports 1 authentication at the moment. 

(2 other are being implemented)

1. get telegram development credentials in telegram API Development Tools from [https://my.telegram.org/apps](https://my.telegram.org/apps)

2. Create a `config.ini` file with your Telegram API credentials like this:

```ini
[Telegram]

# you can get telegram development credentials in telegram API Development Tools
api_id = 1234566
api_hash = a24adjfakjdfakjshdflkajsbdflk
phone = +905064004949 # use full phone number including + and country code
username = 'powerpuffdude'

```


## Quick Start

### List All Group Chats 

This is required for finding chat id for the chat of interest. 

```python
from tgdata import TgData
import asyncio

async def main():
    # Initialize the client
    tg = TgData("config.ini")
    
    # List available groups and channels
    groups = await tg.list_groups()

    print(groups)

```

Outputs:

```
Python Devs 10012312313
```


### Get all messages of a chat 

Once you optain chat id, you can use it to get all messages. 
Upto 2500 messages you will not see limiting from Telegram. 
If group is really active (+20 messages each day for over a year) then it is better to use batch logic. 


```python
from tgdata import TgData
import asyncio

async def main():
    # Initialize the client
    tg = TgData("config.ini")

    # Fetch messages from a specific group
    messages = await tg.get_messages(
        group_id=-1001234567890,  # Your group ID
        limit=1000,
        with_progress=True
    )
    
    # Export to CSV
    tg.export_messages(messages, "messages.csv")

asyncio.run(main())
```

### Get message count of a chat 



```python
from tgdata import TgData
import asyncio

async def main():
    # Initialize the client
    tg = TgData("config.ini")

    # Fetch messages from a specific group
    message_count = await tg.get_message_count(
        group_id=-1001234567890,  # Your group ID
      
    )

    print(message_count)

asyncio.run(main())
```




## Advanced Usage

### get_messages with start_date parameter

```python

    tg = TgData("config.ini")
    # Fetch recent messages for ETL processing
    yesterday = datetime.now() - timedelta(days=1)
    messages = await tg.get_messages(
        group_id=-1001234567890,
        start_date=yesterday,
        with_progress=True
    )
    

```

### Incremental Message Fetching

```python
from tgdata import TgData

async def incremental_fetch():
    tg = TgData("config.ini")
    
    # Get the latest message ID from your storage, or db
    last_processed_id = load_checkpoint()  # Your implementation
    
    # Fetch only messages after that ID
    new_messages = await tg.get_messages(
        group_id=-1001234567890,
        after_id=last_processed_id
    )

    save_checkpoint(new_messages['MessageId'].max())   # Your implementation


asyncio.run(incremental_fetch())
```

### Progress Monitoring

```python
async def monitor_extraction():
    tg = TgData()
    
    def progress_callback(current, total, rate):
        percent = (current / total * 100) if total else 0
        print(f"Progress: {current}/{total} ({percent:.1f}%) - {rate:.1f} msg/s")
    
    messages = await tg.get_messages(
        group_id=-1001234567890,
        limit=10000,
        progress_callback=progress_callback
    )
```

### Custom callback 




### Polling for New Messages

```python
async def poll_messages():
    tg = TgData()
    
    # Define callback for new messages
    async def process_batch(messages_df):
        print(f"Got {len(messages_df)} new messages")
        # Process messages here
    
    # Poll every 30 seconds
    await tg.poll_for_messages(
        group_id=-1001234567890,
        interval=30,
        callback=process_batch,
        max_iterations=10  # Stop after 10 polls
    )
```


###  on_new_message method


### Performance Tips

- Use connection pooling for parallel operations
- Implement checkpoint logic for incremental processing
- Implement progress callbacks for visibility
- Export data incrementally for large datasets

## Requirements

- Python 3.7+
- Telegram API credentials (not bot tokens)
- Group/channel membership

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
