# TeleConnector

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PyPI Version](https://img.shields.io/pypi/v/teleconnector)

A robust Python package for seamless Telegram bot interactions with advanced file handling capabilities.

## Features

-  Send messages and files to Telegram chats
-  Listen for incoming messages and files in real-time
-  Automatic file saving with custom paths via captions
-  Comprehensive error handling and validation
-  Configurable timeouts for all operations
-  Supports both individual chats and groups

## Installation

```bash
pip install teleconnector
```

## Quick Start

### 1. Sending Messages

```python
from teleconnector import send_message

bot_token = "YOUR_BOT_TOKEN"
chat_id = "TARGET_CHAT_ID"

message = "Hello World"  

try:
    result = send_message(message, bot_token, chat_id)
    print("✅ Message sent successfully!")
    print("🆔 Message ID:", result['result']['message_id'])
except Exception as e:
    print(f"❌ Error while sending message: {e}")


```

### Listen For Messages

```python
from teleconnector import listen_for_messages

bot_token = "YOUR_BOT_TOKEN"
chat_id = "TARGET_CHAT_ID"

try:
    print("📡 Listening for new messages... (Press CTRL+C to stop)")
    for message in listen_for_messages(bot_token, chat_id):
        from_user = message.get('from', {})
        name = from_user.get('first_name', 'Unknown')
        text = message.get('text', '')
        print(f"💬 New message from {name}: {text}")
except KeyboardInterrupt:
    print("\n🛑 Listener stopped by user.")
except Exception as e:
    print(f"❌ Error while listening for messages: {e}")

```

### 3. Sending File

```python
from teleconnector import send_file

bot_token = "YOUR_BOT_TOKEN"
chat_id = "TARGET_CHAT_ID"
file_path = "/path/to/your/file.pdf"
caption = "Here's the document"  

try:
    result = send_file(file_path, bot_token, chat_id, caption=caption)
    print("✅ File sent successfully!")
    print("🆔 File ID:", result['result']['document']['file_id'])
except Exception as e:
    print(f"❌ Error while sending file: {e}")


```



### 4. Receiving and Auto-Saving Files

```python
from teleconnector import listen_for_files

bot_token = "YOUR_BOT_TOKEN"
chat_id = "TARGET_CHAT_ID"
save_directory = "./downloads" 

try:
    print("📡 Listening for incoming files... (Press CTRL+C to stop)")
    for file_info in listen_for_files(bot_token, chat_id, save_dir=save_directory):
        file_name = file_info.get('file_name', 'Unknown')
        file_size = file_info.get('file_size', 0)
        saved_path = file_info.get('saved_path', 'Not saved')
        print(f"📥 Received file: {file_name} ({file_size} bytes)")
        print(f"💾 Saved to: {saved_path}")
except KeyboardInterrupt:
    print("\n🛑 Listener stopped by user.")
except Exception as e:
    print(f"❌ Error while listening for files: {e}")


```

## Error Handling

The package raises specific exceptions you can catch:

```python
from teleconnector import send_message, TelegramAPIError

bot_token = "YOUR_BOT_TOKEN"
chat_id = "TARGET_CHAT_ID"

try:
    response = send_message("Test message", bot_token, chat_id)
    print("Success:", response)
except TelegramAPIError as e:
    print("Telegram API Error:", e)
except ValueError as e:
    print("Invalid parameters:", e)
except Exception as e:
    print("Unexpected error:", e)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
<a href="https://mrfidal.in">GitHub</a>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
