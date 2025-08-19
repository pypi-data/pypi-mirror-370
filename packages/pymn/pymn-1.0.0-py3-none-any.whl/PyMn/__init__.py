"""
PyMn - کتابخانه قدرتمند برای ساخت ربات‌های تلگرام

این کتابخانه امکانات کاملی برای ساخت ربات‌های تلگرام فراهم می‌کند
با API ساده و قدرتمند که توسط DevMoEiN ساخته شده است.
"""

__version__ = "1.0.0"
__author__ = "DevMoEiN"
__email__ = "your-email@example.com"

# Import کلاس‌های اصلی
from .bot import Bot
from .types import *
from .keyboards import InlineKeyboard, ReplyKeyboard
from .exceptions import *
from .utils import *

# تنظیم __all__ برای import *
__all__ = [
    "Bot",
    "InlineKeyboard", 
    "ReplyKeyboard",
    "Message",
    "User", 
    "Chat",
    "CallbackQuery",
    "Update",
    "PyMnException",
    "BotException",
    "APIException",
    "NetworkException",
    "format_text",
    "escape_markdown",
    "parse_command",
    "validate_token",
    "get_file_size",
    "is_valid_chat_id"
]

# پیام خوش‌آمدگویی
def welcome():
    """نمایش پیام خوش‌آمدگویی"""
    print(f"""
🚀 PyMn v{__version__} - کتابخانه ربات‌های تلگرام
📧 ساخته شده توسط: {__author__}
🌟 GitHub: https://github.com/DevMoEiN/PyMn

برای شروع:
import PyMn
bot = PyMn.Bot("YOUR_TOKEN")

مستندات کامل: https://github.com/DevMoEiN/PyMn/wiki
    """)

# نمایش پیام هنگام import
if __name__ != "__main__":
    welcome()
