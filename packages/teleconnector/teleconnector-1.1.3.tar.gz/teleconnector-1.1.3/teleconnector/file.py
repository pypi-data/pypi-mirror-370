import requests
import os
from .exceptions import TelegramAPIError

def send_file(file_path, bot_token, chat_id, caption=None, parse_mode=None):
    if not bot_token or not str(bot_token).strip():
        raise ValueError("Bot token cannot be empty")
    if not chat_id:
        raise ValueError("Chat ID cannot be empty")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    try:
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {
                'chat_id': str(chat_id),
                'caption': caption,
                'parse_mode': parse_mode
            }
            response = requests.post(url, files=files, data=data, timeout=20)
            response.raise_for_status()
            data = response.json()
            if not data.get('ok', False):
                error_description = data.get('description', 'Unknown error')
                raise TelegramAPIError(f"Telegram API error: {error_description}")
            return data
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to send file: {str(e)}")

def listen_for_files(bot_token, chat_id=None, timeout=30, save_dir=None):
    if not bot_token or not str(bot_token).strip():
        raise ValueError("Bot token cannot be empty")
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    offset = 0
    try:
        while True:
            params = {
                'offset': offset,
                'timeout': timeout,
                'allowed_updates': ['message']
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
                if 'document' in message:
                    file_data = {
                        'file_id': message['document']['file_id'],
                        'file_name': message['document'].get('file_name'),
                        'file_size': message['document'].get('file_size'),
                        'mime_type': message['document'].get('mime_type'),
                        'chat_id': message['chat']['id'],
                        'caption': message.get('caption')
                    }
                    if not chat_id or str(message['chat']['id']) == str(chat_id):
                        if save_dir:
                            os.makedirs(save_dir, exist_ok=True)
                            file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_data['file_id']}"
                            file_response = requests.get(file_url)
                            file_path = file_response.json()['result']['file_path']
                            download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                            local_filename = os.path.join(save_dir, file_data['file_name'] or os.path.basename(file_path))
                            with requests.get(download_url, stream=True) as r:
                                r.raise_for_status()
                                with open(local_filename, 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            file_data['saved_path'] = local_filename
                        yield file_data
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to listen for files: {str(e)}")