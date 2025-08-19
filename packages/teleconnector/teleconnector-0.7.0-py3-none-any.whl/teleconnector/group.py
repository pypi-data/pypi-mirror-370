import requests
import time
from .exceptions import TelegramAPIError

def listen_for_messages(bot_token, chat_id=None):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    offset = 0
    try:
        while True:
            params = {'offset': offset, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            data = response.json()
            if not data.get('ok'):
                raise TelegramAPIError(data.get('description', 'Unknown error'))
            for update in data.get('result', []):
                offset = update['update_id'] + 1
                message = update.get('message', {})
                if not chat_id or str(message.get('chat', {}).get('id')) == str(chat_id):
                    yield {
                        'update_id': update['update_id'],
                        'message': message,
                        'timestamp': update.get('message', {}).get('date')
                    }
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to listen for messages: {str(e)}")