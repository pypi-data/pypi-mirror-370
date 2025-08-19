import requests
import os
from .exceptions import TelegramAPIError

def send_file(file_path, bot_token, chat_id, caption=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': str(chat_id), 'caption': caption}
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"File sending failed: {str(e)}")

def listen_for_files(bot_token, timeout=30):
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
                if 'document' in message:
                    yield {
                        'file_id': message['document']['file_id'],
                        'file_name': message['document'].get('file_name'),
                        'file_size': message['document'].get('file_size'),
                        'mime_type': message['document'].get('mime_type'),
                        'chat_id': message['chat']['id'],
                        'caption': message.get('caption')
                    }
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"File listening failed: {str(e)}")