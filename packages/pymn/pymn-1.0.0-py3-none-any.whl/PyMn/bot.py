"""
کلاس اصلی Bot برای مدیریت ربات تلگرام
"""

import asyncio
import aiohttp
import json
import logging
from typing import Optional, Callable, List, Dict, Any, Union
from .types import Update, Message, CallbackQuery, User, Chat
from .exceptions import BotException, APIException, NetworkException
from .utils import validate_token, format_text


class Bot:
    """
    کلاس اصلی برای ساخت و مدیریت ربات تلگرام
    
    مثال استفاده:
        bot = Bot("YOUR_BOT_TOKEN")
        
        @bot.message_handler()
        async def handle_message(message):
            await bot.send_message(message.chat.id, "سلام!")
            
        bot.run()
    """
    
    def __init__(self, token: str, parse_mode: str = "HTML"):
        """
        ایجاد یک ربات جدید
        
        Args:
            token: توکن ربات دریافتی از BotFather
            parse_mode: حالت پردازش متن (HTML, Markdown, یا None)
        """
        if not validate_token(token):
            raise BotException("توکن ربات نامعتبر است!")
            
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.parse_mode = parse_mode
        self.session: Optional[aiohttp.ClientSession] = None
        
        # handlers
        self._message_handlers: List[Dict[str, Any]] = []
        self._callback_handlers: List[Callable] = []
        self._command_handlers: Dict[str, Callable] = {}
        self._middleware: List[Callable] = []
        
        # تنظیمات
        self.running = False
        self.offset = 0
        self.timeout = 30
        
        # لاگ
        self.logger = logging.getLogger(f"PyMn.Bot")
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """دریافت session برای درخواست‌های HTTP"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def _make_request(self, method: str, data: Dict = None, files: Dict = None) -> Dict:
        """
        ارسال درخواست به API تلگرام
        
        Args:
            method: نام متود API
            data: داده‌های ارسالی
            files: فایل‌های ارسالی
            
        Returns:
            پاسخ API
        """
        url = f"{self.api_url}/{method}"
        session = await self._get_session()
        
        try:
            if files:
                form_data = aiohttp.FormData()
                for key, value in (data or {}).items():
                    form_data.add_field(key, str(value))
                for key, file_data in files.items():
                    form_data.add_field(key, file_data)
                
                async with session.post(url, data=form_data) as response:
                    result = await response.json()
            else:
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    
            if not result.get("ok"):
                error_code = result.get("error_code", 0)
                description = result.get("description", "خطای نامشخص")
                raise APIException(f"خطای API {error_code}: {description}")
                
            return result.get("result")
            
        except aiohttp.ClientError as e:
            raise NetworkException(f"خطای شبکه: {e}")
        except json.JSONDecodeError:
            raise APIException("پاسخ نامعتبر از سرور")
            
    # متودهای اصلی API
    
    async def get_me(self) -> User:
        """دریافت اطلاعات ربات"""
        result = await self._make_request("getMe")
        return User.from_dict(result)
        
    async def send_message(
        self, 
        chat_id: Union[int, str], 
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict] = None,
        disable_web_page_preview: bool = False,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None
    ) -> Message:
        """
        ارسال پیام متنی
        
        Args:
            chat_id: شناسه چت یا کانال
            text: متن پیام
            parse_mode: حالت پردازش متن
            reply_markup: کیبورد
            disable_web_page_preview: غیرفعال کردن پیش‌نمایش لینک
            disable_notification: ارسال بی‌صدا
            reply_to_message_id: پاسخ به پیام
            
        Returns:
            پیام ارسال شده
        """
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode or self.parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification
        }
        
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
            
        result = await self._make_request("sendMessage", data)
        return Message.from_dict(result)
        
    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict] = None
    ) -> Message:
        """ارسال عکس"""
        data = {
            "chat_id": chat_id,
            "parse_mode": parse_mode or self.parse_mode
        }
        
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        files = None
        if isinstance(photo, bytes):
            files = {"photo": photo}
        else:
            data["photo"] = photo
            
        result = await self._make_request("sendPhoto", data, files)
        return Message.from_dict(result)
        
    async def send_document(
        self,
        chat_id: Union[int, str],
        document: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict] = None
    ) -> Message:
        """ارسال فایل"""
        data = {
            "chat_id": chat_id,
            "parse_mode": parse_mode or self.parse_mode
        }
        
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        files = None
        if isinstance(document, bytes):
            files = {"document": document}
        else:
            data["document"] = document
            
        result = await self._make_request("sendDocument", data, files)
        return Message.from_dict(result)
        
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
        url: Optional[str] = None,
        cache_time: int = 0
    ) -> bool:
        """پاسخ به callback query"""
        data = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
            "cache_time": cache_time
        }
        
        if text:
            data["text"] = text
        if url:
            data["url"] = url
            
        await self._make_request("answerCallbackQuery", data)
        return True
        
    async def edit_message_text(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict] = None
    ) -> Union[Message, bool]:
        """ویرایش متن پیام"""
        data = {
            "text": text,
            "parse_mode": parse_mode or self.parse_mode
        }
        
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data["chat_id"] = chat_id
            data["message_id"] = message_id
            
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        result = await self._make_request("editMessageText", data)
        
        if isinstance(result, dict):
            return Message.from_dict(result)
        return result
        
    # Handler methods
    
    def message_handler(self, commands: Optional[List[str]] = None, content_types: Optional[List[str]] = None):
        """دکوراتور برای مدیریت پیام‌ها"""
        def decorator(func: Callable):
            handler_dict = {
                "function": func,
                "commands": commands or [],
                "content_types": content_types or ["text"]
            }
            self._message_handlers.append(handler_dict)
            return func
        return decorator
        
    def callback_query_handler(self):
        """دکوراتور برای مدیریت callback query ها"""
        def decorator(func: Callable):
            self._callback_handlers.append(func)
            return func
        return decorator
        
    def command_handler(self, command: str):
        """دکوراتور برای مدیریت کامندها"""
        def decorator(func: Callable):
            self._command_handlers[command] = func
            return func
        return decorator
        
    def middleware(self):
        """دکوراتور برای middleware"""
        def decorator(func: Callable):
            self._middleware.append(func)
            return func
        return decorator
        
    # متودهای پردازش
    
    async def _process_update(self, update: Update):
        """پردازش یک آپدیت"""
        try:
            # اجرای middleware
            for middleware_func in self._middleware:
                result = await middleware_func(update)
                if result is False:  # اگر middleware False برگردوند، متوقف شو
                    return
                    
            # پردازش پیام
            if update.message:
                await self._process_message(update.message)
                
            # پردازش callback query
            elif update.callback_query:
                await self._process_callback_query(update.callback_query)
                
        except Exception as e:
            self.logger.error(f"خطا در پردازش آپدیت: {e}")
            
    async def _process_message(self, message: Message):
        """پردازش پیام"""
        # بررسی کامند
        if message.text and message.text.startswith("/"):
            command = message.text.split()[0][1:]  # حذف /
            if command in self._command_handlers:
                await self._command_handlers[command](message)
                return
                
        # بررسی message handlers
        for handler in self._message_handlers:
            # بررسی content type
            if message.content_type not in handler["content_types"]:
                continue
                
            # بررسی کامند (اگر تعریف شده)
            if handler["commands"]:
                if not message.text or not message.text.startswith("/"):
                    continue
                command = message.text.split()[0][1:]
                if command not in handler["commands"]:
                    continue
                    
            # اجرای handler
            await handler["function"](message)
            break
            
    async def _process_callback_query(self, callback_query: CallbackQuery):
        """پردازش callback query"""
        for handler in self._callback_handlers:
            await handler(callback_query)
            
    async def get_updates(self) -> List[Update]:
        """دریافت آپدیت‌ها از تلگرام"""
        data = {
            "offset": self.offset,
            "timeout": self.timeout,
            "allowed_updates": ["message", "callback_query"]
        }
        
        try:
            results = await self._make_request("getUpdates", data)
            updates = [Update.from_dict(update_data) for update_data in results]
            
            if updates:
                self.offset = updates[-1].update_id + 1
                
            return updates
            
        except Exception as e:
            self.logger.error(f"خطا در دریافت آپدیت‌ها: {e}")
            return []
            
    async def start_polling(self):
        """شروع polling برای دریافت آپدیت‌ها"""
        self.running = True
        self.logger.info("🚀 ربات شروع شد - در حال گوش دادن...")
        
        while self.running:
            try:
                updates = await self.get_updates()
                
                # پردازش همزمان آپدیت‌ها
                tasks = [self._process_update(update) for update in updates]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
            except KeyboardInterrupt:
                self.logger.info("⏹️ ربات متوقف شد")
                break
            except Exception as e:
                self.logger.error(f"خطا در polling: {e}")
                await asyncio.sleep(1)  # صبر قبل از تلاش مجدد
                
    def run(self):
        """اجرای ربات (blocking)"""
        try:
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            pass
        finally:
            asyncio.run(self.close())
            
    async def close(self):
        """بستن session و منابع"""
        if self.session and not self.session.closed:
            await self.session.close()
        self.running = False
        
    def stop(self):
        """متوقف کردن ربات"""
        self.running = False
