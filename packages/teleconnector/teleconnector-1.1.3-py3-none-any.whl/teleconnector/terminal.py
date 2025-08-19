import requests
from .exceptions import TelegramAPIError

def send_message(text, bot_token, chat_id, parse_mode=None, disable_web_page_preview=None):
    if not bot_token or not str(bot_token).strip():
        raise ValueError("Bot token cannot be empty")
    if not chat_id:
        raise ValueError("Chat ID cannot be empty")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': str(chat_id),
        'text': text
    }
    if parse_mode:
        payload['parse_mode'] = parse_mode
    if disable_web_page_preview is not None:
        payload['disable_web_page_preview'] = disable_web_page_preview
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get('ok', False):
            error_description = data.get('description', 'Unknown error')
            raise TelegramAPIError(f"Telegram API error: {error_description}")
        return data
    except requests.exceptions.RequestException as e:
        raise TelegramAPIError(f"Failed to send message: {str(e)}")