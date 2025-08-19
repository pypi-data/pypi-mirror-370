"""
کلاس‌های مربوط به خطاها و exceptions
"""


class PyMnException(Exception):
    """کلاس پایه برای تمام خطاهای PyMn"""
    pass


class BotException(PyMnException):
    """خطاهای مربوط به ربات"""
    pass


class APIException(PyMnException):
    """خطاهای مربوط به API تلگرام"""
    
    def __init__(self, message: str, error_code: int = 0):
        """
        ساخت خطای API
        
        Args:
            message: پیام خطا
            error_code: کد خطای تلگرام
        """
        super().__init__(message)
        self.error_code = error_code


class NetworkException(PyMnException):
    """خطاهای مربوط به شبکه"""
    pass


class ValidationException(PyMnException):
    """خطاهای مربوط به اعتبارسنجی داده‌ها"""
    pass


class TimeoutException(PyMnException):
    """خطاهای مربوط به timeout"""
    pass


class FileException(PyMnException):
    """خطاهای مربوط به فایل‌ها"""
    pass


class TokenException(BotException):
    """خطاهای مربوط به توکن ربات"""
    pass


class ChatNotFoundException(APIException):
    """خطای پیدا نشدن چت"""
    pass


class MessageNotFoundException(APIException):
    """خطای پیدا نشدن پیام"""
    pass


class UserBlockedException(APIException):
    """خطای بلاک شدن توسط کاربر"""
    pass


class RateLimitException(APIException):
    """خطای محدودیت نرخ درخواست"""
    
    def __init__(self, message: str, retry_after: int = 0):
        """
        ساخت خطای rate limit
        
        Args:
            message: پیام خطا
            retry_after: زمان انتظار تا درخواست بعدی (ثانیه)
        """
        super().__init__(message)
        self.retry_after = retry_after
