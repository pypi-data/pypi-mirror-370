from .terminal import send_message
from .group import listen_for_messages
from .file import send_file, listen_for_files

__version__ = "1.0.1"
__all__ = [
    'send_message',
    'listen_for_messages',
    'send_file',
    'listen_for_files',
    'TelegramAPIError'
]