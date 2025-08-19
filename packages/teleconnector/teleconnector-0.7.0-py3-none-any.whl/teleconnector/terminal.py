import requests
from .exceptions import TelegramAPIError

def send_message(text, bot_token, chat_id, parse_mode=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': str(chat_id),
        'text': text,
        'parse_mode': parse_mode
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get('ok'):
            raise TelegramAPIError(data.get('description', 'Unknown error'))
        return data
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to send message: {str(e)}")