import requests
import time
from .exceptions import TelegramAPIError

def listen_for_messages(bot_token, chat_id=None, timeout=30, allowed_updates=None):
    if not bot_token or not str(bot_token).strip():
        raise ValueError("Bot token cannot be empty")
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    offset = 0
    try:
        while True:
            params = {
                'offset': offset,
                'timeout': timeout,
                'allowed_updates': allowed_updates or ['message']
            }
            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            data = response.json()
            if not data.get('ok', False):
                error_description = data.get('description', 'Unknown error')
                raise TelegramAPIError(f"Telegram API error: {error_description}")
            for update in data.get('result', []):
                offset = update['update_id'] + 1
                message = update.get('message', {})
                if not chat_id or str(message.get('chat', {}).get('id')) == str(chat_id):
                    yield {
                        'update_id': update['update_id'],
                        'message_id': message.get('message_id'),
                        'text': message.get('text'),
                        'chat': message.get('chat', {}),
                        'date': message.get('date'),
                        'from': message.get('from'),
                        'entities': message.get('entities', [])
                    }
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to listen for messages: {str(e)}")