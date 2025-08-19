import requests
from .exceptions import TelegramAPIError

def send_message(message, bot_token, chat_id, parse_mode=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': str(chat_id),
        'text': message,
        'parse_mode': parse_mode
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Message sending failed: {str(e)}")