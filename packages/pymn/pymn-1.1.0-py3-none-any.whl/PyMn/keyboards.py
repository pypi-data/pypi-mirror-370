from typing import List, Optional, Dict, Any, Union


class InlineKeyboardButton:
    """Button class compatible with python-telegram-bot style"""
    
    def __init__(self, text: str, url: Optional[str] = None, callback_data: Optional[str] = None,
                 switch_inline_query: Optional[str] = None, switch_inline_query_current_chat: Optional[str] = None,
                 pay: Optional[bool] = None, login_url: Optional[Dict] = None, 
                 web_app: Optional[Dict] = None, **kwargs):
        self.text = text
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.pay = pay
        self.login_url = login_url
        self.web_app = web_app
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def to_dict(self) -> Dict[str, Any]:
        data = {"text": self.text}
        
        if self.url:
            data["url"] = self.url
        if self.callback_data:
            data["callback_data"] = self.callback_data
        if self.switch_inline_query is not None:
            data["switch_inline_query"] = self.switch_inline_query
        if self.switch_inline_query_current_chat is not None:
            data["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat
        if self.pay:
            data["pay"] = self.pay
        if self.login_url:
            data["login_url"] = self.login_url
        if self.web_app:
            data["web_app"] = self.web_app
            
        return data


class InlineKeyboardMarkup:
    """Keyboard markup compatible with python-telegram-bot style"""
    
    def __init__(self, inline_keyboard: List[List[InlineKeyboardButton]], **kwargs):
        if isinstance(inline_keyboard[0][0], InlineKeyboardButton):
            self.inline_keyboard = [[btn.to_dict() for btn in row] for row in inline_keyboard]
        else:
            self.inline_keyboard = inline_keyboard
            
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    @classmethod
    def from_button(cls, button: InlineKeyboardButton) -> 'InlineKeyboardMarkup':
        return cls([[button]])
        
    @classmethod
    def from_row(cls, *buttons: InlineKeyboardButton) -> 'InlineKeyboardMarkup':
        return cls([list(buttons)])
        
    @classmethod
    def from_column(cls, *buttons: InlineKeyboardButton) -> 'InlineKeyboardMarkup':
        return cls([[button] for button in buttons])
        
    def to_dict(self) -> Dict[str, Any]:
        return {"inline_keyboard": self.inline_keyboard}


class InlineButton:
    """کلاس دکمه inline"""
    
    def __init__(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        pay: Optional[bool] = None
    ):
        """
        ساخت دکمه inline
        
        Args:
            text: متن دکمه
            callback_data: داده callback
            url: لینک دکمه
            switch_inline_query: تغییر به حالت inline
            switch_inline_query_current_chat: تغییر به inline در همین چت
            pay: دکمه پرداخت
        """
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.pay = pay
        
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        button = {"text": self.text}
        
        if self.callback_data:
            button["callback_data"] = self.callback_data
        elif self.url:
            button["url"] = self.url
        elif self.switch_inline_query is not None:
            button["switch_inline_query"] = self.switch_inline_query
        elif self.switch_inline_query_current_chat is not None:
            button["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat
        elif self.pay:
            button["pay"] = self.pay
            
        return button


class InlineKeyboard:
    """کلاس کیبورد inline"""
    
    def __init__(self):
        """ساخت کیبورد inline خالی"""
        self.keyboard: List[List[InlineButton]] = []
        
    def add_button(
        self,
        text: str,
        callback_data: Optional[str] = None,
        url: Optional[str] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        pay: Optional[bool] = None
    ) -> 'InlineKeyboard':
        """
        اضافه کردن دکمه در ردیف جدید
        
        Args:
            text: متن دکمه
            callback_data: داده callback
            url: لینک دکمه
            switch_inline_query: تغییر به حالت inline
            switch_inline_query_current_chat: تغییر به inline در همین چت
            pay: دکمه پرداخت
            
        Returns:
            خود کیبورد برای method chaining
        """
        button = InlineButton(
            text=text,
            callback_data=callback_data,
            url=url,
            switch_inline_query=switch_inline_query,
            switch_inline_query_current_chat=switch_inline_query_current_chat,
            pay=pay
        )
        self.keyboard.append([button])
        return self
        
    def add_row(self, *buttons: InlineButton) -> 'InlineKeyboard':
        """
        اضافه کردن ردیف از دکمه‌ها
        
        Args:
            buttons: دکمه‌های ردیف
            
        Returns:
            خود کیبورد برای method chaining
        """
        self.keyboard.append(list(buttons))
        return self
        
    def add_buttons_row(self, *button_data: tuple) -> 'InlineKeyboard':
        """
        اضافه کردن ردیف دکمه‌ها با داده‌های ساده
        
        Args:
            button_data: تاپل‌های (text, callback_data) یا (text, url)
            
        Returns:
            خود کیبورد برای method chaining
            
        مثال:
            keyboard.add_buttons_row(
                ("دکمه 1", "data1"),
                ("دکمه 2", "data2")
            )
        """
        buttons = []
        for data in button_data:
            if len(data) == 2:
                text, callback_or_url = data
                if callback_or_url.startswith("http"):
                    button = InlineButton(text=text, url=callback_or_url)
                else:
                    button = InlineButton(text=text, callback_data=callback_or_url)
                buttons.append(button)
                
        if buttons:
            self.keyboard.append(buttons)
        return self
        
    def add_url_button(self, text: str, url: str) -> 'InlineKeyboard':
        """اضافه کردن دکمه URL"""
        return self.add_button(text=text, url=url)
        
    def add_callback_button(self, text: str, callback_data: str) -> 'InlineKeyboard':
        """اضافه کردن دکمه callback"""
        return self.add_button(text=text, callback_data=callback_data)
        
    def add_switch_inline_button(self, text: str, query: str = "", current_chat: bool = False) -> 'InlineKeyboard':
        """اضافه کردن دکمه switch inline"""
        if current_chat:
            return self.add_button(text=text, switch_inline_query_current_chat=query)
        else:
            return self.add_button(text=text, switch_inline_query=query)
            
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary برای ارسال"""
        return {
            "inline_keyboard": [
                [button.to_dict() for button in row]
                for row in self.keyboard
            ]
        }
        
    def clear(self) -> 'InlineKeyboard':
        """پاک کردن تمام دکمه‌ها"""
        self.keyboard.clear()
        return self
        
    @classmethod
    def from_buttons(cls, buttons: List[List[tuple]]) -> 'InlineKeyboard':
        """
        ساخت کیبورد از لیست دکمه‌ها
        
        Args:
            buttons: لیست از ردیف‌های دکمه (text, callback_data/url)
            
        Returns:
            کیبورد ساخته شده
            
        مثال:
            keyboard = InlineKeyboard.from_buttons([
                [("دکمه 1", "data1"), ("دکمه 2", "data2")],
                [("لینک", "https://google.com")]
            ])
        """
        keyboard = cls()
        for row in buttons:
            keyboard.add_buttons_row(*row)
        return keyboard


class KeyboardButton:
    """کلاس دکمه معمولی"""
    
    def __init__(
        self,
        text: str,
        request_contact: bool = False,
        request_location: bool = False,
        request_poll: Optional[Dict] = None
    ):
        """
        ساخت دکمه معمولی
        
        Args:
            text: متن دکمه
            request_contact: درخواست شماره تماس
            request_location: درخواست مکان
            request_poll: درخواست نظرسنجی
        """
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location
        self.request_poll = request_poll
        
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        button = {"text": self.text}
        
        if self.request_contact:
            button["request_contact"] = True
        if self.request_location:
            button["request_location"] = True
        if self.request_poll:
            button["request_poll"] = self.request_poll
            
        return button


class ReplyKeyboard:
    """کلاس کیبورد معمولی"""
    
    def __init__(
        self,
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
        selective: bool = False,
        placeholder: Optional[str] = None
    ):
        """
        ساخت کیبورد معمولی
        
        Args:
            resize_keyboard: تنظیم اندازه خودکار
            one_time_keyboard: مخفی شدن بعد از استفاده
            selective: نمایش برای کاربران خاص
            placeholder: متن راهنما
        """
        self.keyboard: List[List[KeyboardButton]] = []
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective
        self.input_field_placeholder = placeholder
        
    def add_button(
        self,
        text: str,
        request_contact: bool = False,
        request_location: bool = False,
        request_poll: Optional[Dict] = None
    ) -> 'ReplyKeyboard':
        """اضافه کردن دکمه در ردیف جدید"""
        button = KeyboardButton(
            text=text,
            request_contact=request_contact,
            request_location=request_location,
            request_poll=request_poll
        )
        self.keyboard.append([button])
        return self
        
    def add_row(self, *buttons: KeyboardButton) -> 'ReplyKeyboard':
        """اضافه کردن ردیف از دکمه‌ها"""
        self.keyboard.append(list(buttons))
        return self
        
    def add_buttons_row(self, *texts: str) -> 'ReplyKeyboard':
        """اضافه کردن ردیف دکمه‌ها با متن ساده"""
        buttons = [KeyboardButton(text) for text in texts]
        self.keyboard.append(buttons)
        return self
        
    def add_contact_button(self, text: str = "📱 ارسال شماره تماس") -> 'ReplyKeyboard':
        """اضافه کردن دکمه درخواست شماره تماس"""
        return self.add_button(text=text, request_contact=True)
        
    def add_location_button(self, text: str = "📍 ارسال مکان") -> 'ReplyKeyboard':
        """اضافه کردن دکمه درخواست مکان"""
        return self.add_button(text=text, request_location=True)
        
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary برای ارسال"""
        markup = {
            "keyboard": [
                [button.to_dict() for button in row]
                for row in self.keyboard
            ],
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.one_time_keyboard,
            "selective": self.selective
        }
        
        if self.input_field_placeholder:
            markup["input_field_placeholder"] = self.input_field_placeholder
            
        return markup
        
    def clear(self) -> 'ReplyKeyboard':
        """پاک کردن تمام دکمه‌ها"""
        self.keyboard.clear()
        return self
        
    @classmethod
    def from_buttons(cls, buttons: List[List[str]], **kwargs) -> 'ReplyKeyboard':
        """
        ساخت کیبورد از لیست متن‌ها
        
        Args:
            buttons: لیست از ردیف‌های متن دکمه
            **kwargs: پارامترهای کیبورد
            
        Returns:
            کیبورد ساخته شده
            
        مثال:
            keyboard = ReplyKeyboard.from_buttons([
                ["دکمه 1", "دکمه 2"],
                ["دکمه 3"]
            ])
        """
        keyboard = cls(**kwargs)
        for row in buttons:
            keyboard.add_buttons_row(*row)
        return keyboard


class ReplyKeyboardRemove:
    """کلاس حذف کیبورد"""
    
    def __init__(self, selective: bool = False):
        """
        ساخت دستور حذف کیبورد
        
        Args:
            selective: حذف برای کاربران خاص
        """
        self.remove_keyboard = True
        self.selective = selective
        
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        return {
            "remove_keyboard": self.remove_keyboard,
            "selective": self.selective
        }


class ForceReply:
    def __init__(self, selective: bool = False, placeholder: Optional[str] = None):
        self.force_reply = True
        self.selective = selective
        self.input_field_placeholder = placeholder
        
    def to_dict(self) -> Dict[str, Any]:
        markup = {"force_reply": self.force_reply, "selective": self.selective}
        if self.input_field_placeholder:
            markup["input_field_placeholder"] = self.input_field_placeholder
        return markup



