import os
import requests
from urllib.parse import unquote
from pathlib import Path
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

def listen_for_files(bot_token, timeout=30, save_dir=None):
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
                    file_info = {
                        'file_id': message['document']['file_id'],
                        'file_name': message['document'].get('file_name'),
                        'file_size': message['document'].get('file_size'),
                        'mime_type': message['document'].get('mime_type'),
                        'chat_id': message['chat']['id'],
                        'caption': message.get('caption'),
                        'message_id': message.get('message_id')
                    }
                    
                    if save_dir and file_info['caption'] and file_info['caption'].startswith('save:'):
                        save_path = file_info['caption'][5:].strip()
                        file_info['saved_path'] = save_file_from_caption(
                            bot_token, 
                            file_info['file_id'], 
                            save_path,
                            file_info.get('file_name', 'file')
                        )
                    
                    yield file_info
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to listen for files: {str(e)}")

def save_file_from_caption(bot_token, file_id, save_path, original_filename=None):
    if not bot_token or not str(bot_token).strip():
        raise ValueError("Bot token cannot be empty")
    
    if not file_id:
        raise ValueError("File ID cannot be empty")
    
    if not save_path:
        raise ValueError("Save path cannot be empty")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        response = requests.get(url)
        response.raise_for_status()
        file_data = response.json()
        
        if not file_data.get('ok', False):
            raise TelegramAPIError(file_data.get('description', 'Failed to get file path'))
        
        file_path = file_data['result']['file_path']
        download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        
        os.makedirs(save_path, exist_ok=True)
        
        filename = original_filename or os.path.basename(file_path)
        full_path = os.path.join(save_path, filename)
        
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(full_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        return full_path
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to download file: {str(e)}")
    except OSError as e:
        raise TelegramAPIError(f"Failed to save file: {str(e)}")