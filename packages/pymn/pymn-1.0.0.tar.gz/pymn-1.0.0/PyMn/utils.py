"""
توابع کمکی و ابزارهای کاربردی PyMn
"""

import re
import os
import mimetypes
import hashlib
import asyncio
from typing import Optional, List, Dict, Any, Union, Callable
from datetime import datetime, timedelta
import json


def validate_token(token: str) -> bool:
    """
    اعتبارسنجی توکن ربات
    
    Args:
        token: توکن ربات
        
    Returns:
        True اگر توکن معتبر باشد
    """
    if not token or not isinstance(token, str):
        return False
        
    # فرمت توکن: xxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    pattern = r'^\d{8,10}:[a-zA-Z0-9_-]{35}$'
    return bool(re.match(pattern, token))


def format_text(text: str, **kwargs) -> str:
    """
    فرمت کردن متن با پارامترها
    
    Args:
        text: متن اصلی
        **kwargs: پارامترهای جایگزین
        
    Returns:
        متن فرمت شده
        
    مثال:
        format_text("سلام {name}، شما {age} سال دارید", name="علی", age=25)
    """
    try:
        return text.format(**kwargs)
    except KeyError as e:
        return text


def escape_markdown(text: str, version: int = 2) -> str:
    """
    escape کردن کاراکترهای خاص markdown
    
    Args:
        text: متن اصلی
        version: نسخه markdown (1 یا 2)
        
    Returns:
        متن escape شده
    """
    if version == 2:
        # MarkdownV2 characters that need to be escaped
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f'\\{char}')
    else:
        # Markdown characters that need to be escaped
        chars = ['_', '*', '[', '`']
        for char in chars:
            text = text.replace(char, f'\\{char}')
            
    return text


def escape_html(text: str) -> str:
    """
    escape کردن کاراکترهای خاص HTML
    
    Args:
        text: متن اصلی
        
    Returns:
        متن escape شده
    """
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;'))


def parse_command(text: str) -> tuple:
    """
    تجزیه کامند و آرگومان‌ها
    
    Args:
        text: متن کامند
        
    Returns:
        (command, args) - کامند و لیست آرگومان‌ها
        
    مثال:
        parse_command("/start hello world") -> ("start", ["hello", "world"])
    """
    if not text or not text.startswith('/'):
        return None, []
        
    parts = text.split()
    command = parts[0][1:]  # حذف /
    args = parts[1:] if len(parts) > 1 else []
    
    return command, args


def get_file_size(file_path: str) -> int:
    """
    دریافت سایز فایل
    
    Args:
        file_path: مسیر فایل
        
    Returns:
        سایز فایل به بایت
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def get_mime_type(file_path: str) -> str:
    """
    دریافت MIME type فایل
    
    Args:
        file_path: مسیر فایل
        
    Returns:
        MIME type فایل
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'


def is_valid_chat_id(chat_id: Union[int, str]) -> bool:
    """
    بررسی معتبر بودن chat_id
    
    Args:
        chat_id: شناسه چت
        
    Returns:
        True اگر معتبر باشد
    """
    if isinstance(chat_id, int):
        return chat_id != 0
    elif isinstance(chat_id, str):
        return bool(chat_id.strip()) and (chat_id.startswith('@') or chat_id.lstrip('-').isdigit())
    return False


def generate_hash(data: str) -> str:
    """
    تولید hash از داده
    
    Args:
        data: داده ورودی
        
    Returns:
        hash SHA256
    """
    return hashlib.sha256(data.encode()).hexdigest()


def chunks(lst: List, n: int) -> List[List]:
    """
    تقسیم لیست به چندین قسمت
    
    Args:
        lst: لیست اصلی
        n: تعداد عناصر در هر قسمت
        
    Returns:
        لیست از قسمت‌ها
        
    مثال:
        chunks([1,2,3,4,5], 2) -> [[1,2], [3,4], [5]]
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def persian_to_english_numbers(text: str) -> str:
    """
    تبدیل اعداد فارسی به انگلیسی
    
    Args:
        text: متن حاوی اعداد فارسی
        
    Returns:
        متن با اعداد انگلیسی
    """
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    
    for persian, english in zip(persian_digits, english_digits):
        text = text.replace(persian, english)
        
    return text


def english_to_persian_numbers(text: str) -> str:
    """
    تبدیل اعداد انگلیسی به فارسی
    
    Args:
        text: متن حاوی اعداد انگلیسی
        
    Returns:
        متن با اعداد فارسی
    """
    english_digits = '0123456789'
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    
    for english, persian in zip(english_digits, persian_digits):
        text = text.replace(english, persian)
        
    return text


def format_file_size(size_bytes: int) -> str:
    """
    فرمت کردن سایز فایل
    
    Args:
        size_bytes: سایز به بایت
        
    Returns:
        سایز فرمت شده (مثلاً "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
        
    return f"{size_bytes:.1f} {size_names[i]}"


def get_username_from_url(url: str) -> Optional[str]:
    """
    استخراج username از URL تلگرام
    
    Args:
        url: لینک تلگرام
        
    Returns:
        username بدون @
    """
    patterns = [
        r't\.me/(\w+)',
        r'telegram\.me/(\w+)',
        r'telegram\.dog/(\w+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    return None


def is_valid_username(username: str) -> bool:
    """
    بررسی معتبر بودن username
    
    Args:
        username: نام کاربری
        
    Returns:
        True اگر معتبر باشد
    """
    if not username:
        return False
        
    # حذف @ در صورت وجود
    username = username.lstrip('@')
    
    # بررسی طول (5-32 کاراکتر)
    if len(username) < 5 or len(username) > 32:
        return False
        
    # بررسی کاراکترها (فقط حروف، اعداد و _)
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


def extract_user_id_from_mention(mention: str) -> Optional[int]:
    """
    استخراج user_id از mention
    
    Args:
        mention: متن mention
        
    Returns:
        user_id یا None
    """
    # مثال: <a href="tg://user?id=123456789">نام</a>
    pattern = r'tg://user\?id=(\d+)'
    match = re.search(pattern, mention)
    
    if match:
        return int(match.group(1))
        
    return None


class RateLimiter:
    """کلاس محدودکننده نرخ درخواست"""
    
    def __init__(self, max_requests: int, time_window: int):
        """
        ساخت rate limiter
        
        Args:
            max_requests: حداکثر درخواست
            time_window: پنجره زمانی (ثانیه)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
        
    def is_allowed(self, key: str) -> bool:
        """
        بررسی مجاز بودن درخواست
        
        Args:
            key: کلید شناسایی (مثلاً user_id)
            
        Returns:
            True اگر مجاز باشد
        """
        now = datetime.now()
        
        if key not in self.requests:
            self.requests[key] = []
            
        # پاک کردن درخواست‌های قدیمی
        cutoff = now - timedelta(seconds=self.time_window)
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        # بررسی تعداد درخواست‌ها
        if len(self.requests[key]) >= self.max_requests:
            return False
            
        # اضافه کردن درخواست جدید
        self.requests[key].append(now)
        return True


class Cache:
    """کلاس کش ساده"""
    
    def __init__(self, ttl: int = 3600):
        """
        ساخت کش
        
        Args:
            ttl: مدت زمان نگهداری (ثانیه)
        """
        self.ttl = ttl
        self.data = {}
        
    def get(self, key: str) -> Any:
        """دریافت از کش"""
        if key in self.data:
            value, timestamp = self.data[key]
            if datetime.now().timestamp() - timestamp < self.ttl:
                return value
            else:
                del self.data[key]
        return None
        
    def set(self, key: str, value: Any):
        """ذخیره در کش"""
        self.data[key] = (value, datetime.now().timestamp())
        
    def delete(self, key: str):
        """حذف از کش"""
        if key in self.data:
            del self.data[key]
            
    def clear(self):
        """پاک کردن کش"""
        self.data.clear()


class Singleton:
    """کلاس Singleton برای ایجاد instance یکتا"""
    
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    دکوراتور تلاش مجدد در صورت خطا
    
    Args:
        max_retries: حداکثر تعداد تلاش
        delay: تاخیر بین تلاش‌ها (ثانیه)
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        await asyncio.sleep(delay * (2 ** attempt))  # exponential backoff
                    
            raise last_exception
            
        return wrapper
    return decorator


def log_execution_time(func: Callable):
    """دکوراتور لاگ زمان اجرا"""
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
            
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️ {func.__name__} executed in {execution_time:.2f} seconds")
        return result
        
    return wrapper


def safe_int(value: Any, default: int = 0) -> int:
    """
    تبدیل ایمن به int
    
    Args:
        value: مقدار ورودی
        default: مقدار پیش‌فرض در صورت خطا
        
    Returns:
        عدد صحیح
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    تبدیل ایمن به float
    
    Args:
        value: مقدار ورودی
        default: مقدار پیش‌فرض در صورت خطا
        
    Returns:
        عدد اعشاری
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def clean_html(text: str) -> str:
    """
    پاک کردن تگ‌های HTML از متن
    
    Args:
        text: متن حاوی HTML
        
    Returns:
        متن بدون تگ‌های HTML
    """
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def truncate_text(text: str, max_length: int = 4096, suffix: str = "...") -> str:
    """
    کوتاه کردن متن
    
    Args:
        text: متن اصلی
        max_length: حداکثر طول
        suffix: پسوند در صورت کوتاه شدن
        
    Returns:
        متن کوتاه شده
    """
    if len(text) <= max_length:
        return text
        
    return text[:max_length - len(suffix)] + suffix


def split_message(text: str, max_length: int = 4096) -> List[str]:
    """
    تقسیم پیام طولانی به چندین قسمت
    
    Args:
        text: متن اصلی
        max_length: حداکثر طول هر قسمت
        
    Returns:
        لیست از قسمت‌های متن
    """
    if len(text) <= max_length:
        return [text]
        
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
            
        # پیدا کردن آخرین فاصله قبل از حد مجاز
        split_point = text[:max_length].rfind(' ')
        if split_point == -1:
            split_point = max_length
            
        parts.append(text[:split_point])
        text = text[split_point:].lstrip()
        
    return parts
