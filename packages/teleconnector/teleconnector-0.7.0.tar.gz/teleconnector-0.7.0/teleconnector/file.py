import os
import requests
from .exceptions import TelegramAPIError

def send_file(file_path, bot_token, chat_id, caption=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': str(chat_id), 'caption': caption}
            response = requests.post(url, files=files, data=data, timeout=20)
            response.raise_for_status()
            data = response.json()
            if not data.get('ok'):
                raise TelegramAPIError(data.get('description', 'Unknown error'))
            return data
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to send file: {str(e)}")

def listen_for_files(bot_token, save_path=None):
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
                if 'document' in message:
                    file_info = {
                        'file_id': message['document']['file_id'],
                        'file_name': message['document'].get('file_name', 'file'),
                        'file_size': message['document'].get('file_size'),
                        'mime_type': message['document'].get('mime_type'),
                        'caption': message.get('caption'),
                        'timestamp': message.get('date'),
                        'chat_id': message['chat']['id']
                    }
                    if save_path:
                        file_info['saved_path'] = download_file(
                            bot_token,
                            file_info['file_id'],
                            os.path.join(save_path, file_info['file_name'])
                        )
                    yield file_info
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to listen for files: {str(e)}")

def download_file(bot_token, file_id, save_path):
    try:
        file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        response = requests.get(file_url)
        response.raise_for_status()
        file_path = response.json()['result']['file_path']
        
        download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        file_response = requests.get(download_url, stream=True)
        file_response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            for chunk in file_response.iter_content(1024):
                f.write(chunk)
        return save_path
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to download file: {str(e)}")