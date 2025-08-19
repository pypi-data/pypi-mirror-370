__version__ = "1.1.0"
__author__ = "DevMoEiN"

from .bot import Bot
from .userbot import UserBot
from .group_manager import GroupManager
from .security_manager import SecurityManager
from .telegram_pro import TelegramPro
from .telegram_extended import TelegramExtended
from .types import *
from .keyboards import InlineKeyboard, ReplyKeyboard, InlineKeyboardButton, InlineKeyboardMarkup
from .exceptions import *
from .utils import *


Update = Update
InlineKeyboardButton = InlineKeyboardButton
InlineKeyboardMarkup = InlineKeyboardMarkup
TelegramBot = Bot
PyMnBot = Bot

# Backward compatibility for old class names
SmartAdmin = GroupManager
AccountManager = SecurityManager
AdvancedFeatures = TelegramPro
UltimateFeatures = TelegramExtended

telegram = type('telegram', (), {
    'Update': Update,
    'InlineKeyboardButton': InlineKeyboardButton,
    'InlineKeyboardMarkup': InlineKeyboardMarkup,
    'Bot': Bot,
    'Message': Message,
    'User': User,
    'Chat': Chat,
    'CallbackQuery': CallbackQuery
})()

__all__ = [

    "Bot", "TelegramBot", "PyMnBot", "UserBot", "GroupManager", "SecurityManager", "TelegramPro", "TelegramExtended",
    "SmartAdmin", "AccountManager", "AdvancedFeatures", "UltimateFeatures",
    

    "InlineKeyboard", "ReplyKeyboard", "InlineKeyboardButton", "InlineKeyboardMarkup",
    "Message", "User", "Chat", "CallbackQuery", "Update", "InlineQuery",
    
 
    "PyMnException", "BotException", "APIException", "NetworkException",
    
   
    "format_text", "escape_html", "parse_command", "validate_token", "chunks", "split_message",
    "create_quick_keyboard", "create_contact_keyboard", "create_location_keyboard",
    "format_user_mention", "format_bold", "format_italic", "format_code",
    "create_progress_bar", "MessageBuilder", "create_status_message",
    
 
    "telegram"
]
