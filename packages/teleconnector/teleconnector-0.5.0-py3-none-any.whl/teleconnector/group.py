import requests
import time
from .exceptions import TelegramAPIError

def listen_for_messages(bot_token, chat_id=None, timeout=30):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    offset = 0
    try:
        while True:
            params = {'offset': offset, 'timeout': timeout}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['ok']:
                raise TelegramAPIError(data.get('description', 'Unknown error'))
            
            for update in data['result']:
                offset = update['update_id'] + 1
                message = update.get('message', {})
                if not chat_id or str(message.get('chat', {}).get('id')) == str(chat_id):
                    yield {
                        'update_id': update['update_id'],
                        'message_id': message.get('message_id'),
                        'text': message.get('text'),
                        'chat': message.get('chat', {}),
                        'date': message.get('date'),
                        'from': message.get('from')
                    }
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Message listening failed: {str(e)}")