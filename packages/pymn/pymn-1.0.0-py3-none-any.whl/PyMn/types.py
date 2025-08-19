"""
کلاس‌های مربوط به انواع داده‌های تلگرام
"""

from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """کلاس کاربر"""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """ساخت User از dictionary"""
        return cls(
            id=data['id'],
            is_bot=data['is_bot'],
            first_name=data['first_name'],
            last_name=data.get('last_name'),
            username=data.get('username'),
            language_code=data.get('language_code'),
            is_premium=data.get('is_premium')
        )
        
    @property
    def full_name(self) -> str:
        """نام کامل کاربر"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
        
    @property
    def mention(self) -> str:
        """منشن کاربر"""
        if self.username:
            return f"@{self.username}"
        return f"<a href='tg://user?id={self.id}'>{self.first_name}</a>"


@dataclass
class Chat:
    """کلاس چت"""
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    pinned_message: Optional['Message'] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        """ساخت Chat از dictionary"""
        return cls(
            id=data['id'],
            type=data['type'],
            title=data.get('title'),
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            description=data.get('description'),
            invite_link=data.get('invite_link')
        )
        
    @property
    def is_private(self) -> bool:
        """چک کردن private بودن چت"""
        return self.type == "private"
        
    @property
    def is_group(self) -> bool:
        """چک کردن group بودن چت"""
        return self.type in ["group", "supergroup"]
        
    @property
    def is_channel(self) -> bool:
        """چک کردن channel بودن چت"""
        return self.type == "channel"


@dataclass
class PhotoSize:
    """کلاس سایز عکس"""
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhotoSize':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            width=data['width'],
            height=data['height'],
            file_size=data.get('file_size')
        )


@dataclass
class Document:
    """کلاس فایل"""
    file_id: str
    file_unique_id: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size')
        )


@dataclass
class Video:
    """کلاس ویدیو"""
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Video':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            width=data['width'],
            height=data['height'],
            duration=data['duration'],
            thumb=PhotoSize.from_dict(data['thumb']) if data.get('thumb') else None,
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size')
        )


@dataclass
class Audio:
    """کلاس صوت"""
    file_id: str
    file_unique_id: str
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Audio':
        return cls(
            file_id=data['file_id'],
            file_unique_id=data['file_unique_id'],
            duration=data['duration'],
            performer=data.get('performer'),
            title=data.get('title'),
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            file_size=data.get('file_size')
        )


@dataclass
class Message:
    """کلاس پیام"""
    message_id: int
    date: int
    chat: Chat
    from_user: Optional[User] = None
    text: Optional[str] = None
    caption: Optional[str] = None
    photo: Optional[List[PhotoSize]] = None
    document: Optional[Document] = None
    video: Optional[Video] = None
    audio: Optional[Audio] = None
    reply_to_message: Optional['Message'] = None
    forward_from: Optional[User] = None
    forward_date: Optional[int] = None
    edit_date: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """ساخت Message از dictionary"""
        # پردازش عکس‌ها
        photo = None
        if data.get('photo'):
            photo = [PhotoSize.from_dict(p) for p in data['photo']]
            
        # پردازش سایر انواع فایل
        document = Document.from_dict(data['document']) if data.get('document') else None
        video = Video.from_dict(data['video']) if data.get('video') else None
        audio = Audio.from_dict(data['audio']) if data.get('audio') else None
        
        # پردازش reply_to_message (بدون عمق زیاد برای جلوگیری از recursion)
        reply_to = None
        if data.get('reply_to_message'):
            reply_data = data['reply_to_message'].copy()
            reply_data.pop('reply_to_message', None)  # جلوگیری از recursion
            reply_to = cls.from_dict(reply_data)
            
        return cls(
            message_id=data['message_id'],
            date=data['date'],
            chat=Chat.from_dict(data['chat']),
            from_user=User.from_dict(data['from']) if data.get('from') else None,
            text=data.get('text'),
            caption=data.get('caption'),
            photo=photo,
            document=document,
            video=video,
            audio=audio,
            reply_to_message=reply_to,
            forward_from=User.from_dict(data['forward_from']) if data.get('forward_from') else None,
            forward_date=data.get('forward_date'),
            edit_date=data.get('edit_date')
        )
        
    @property
    def content_type(self) -> str:
        """نوع محتوای پیام"""
        if self.text:
            return "text"
        elif self.photo:
            return "photo"
        elif self.document:
            return "document"
        elif self.video:
            return "video"
        elif self.audio:
            return "audio"
        else:
            return "unknown"
            
    @property
    def datetime(self) -> datetime:
        """تاریخ پیام به صورت datetime"""
        return datetime.fromtimestamp(self.date)
        
    def is_command(self) -> bool:
        """بررسی کامند بودن پیام"""
        return bool(self.text and self.text.startswith("/"))
        
    def get_command(self) -> Optional[str]:
        """دریافت کامند از پیام"""
        if self.is_command():
            return self.text.split()[0][1:]  # حذف /
        return None
        
    def get_args(self) -> List[str]:
        """دریافت آرگومان‌های کامند"""
        if self.is_command() and self.text:
            parts = self.text.split()[1:]
            return parts
        return []


@dataclass
class CallbackQuery:
    """کلاس callback query"""
    id: str
    from_user: User
    data: Optional[str] = None
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CallbackQuery':
        """ساخت CallbackQuery از dictionary"""
        return cls(
            id=data['id'],
            from_user=User.from_dict(data['from']),
            data=data.get('data'),
            message=Message.from_dict(data['message']) if data.get('message') else None,
            inline_message_id=data.get('inline_message_id')
        )


@dataclass
class InlineQuery:
    """کلاس inline query"""
    id: str
    from_user: User
    query: str
    offset: str
    chat_type: Optional[str] = None
    location: Optional[Dict] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InlineQuery':
        return cls(
            id=data['id'],
            from_user=User.from_dict(data['from']),
            query=data['query'],
            offset=data['offset'],
            chat_type=data.get('chat_type'),
            location=data.get('location')
        )


@dataclass
class Update:
    """کلاس آپدیت"""
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    inline_query: Optional[InlineQuery] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Update':
        """ساخت Update از dictionary"""
        return cls(
            update_id=data['update_id'],
            message=Message.from_dict(data['message']) if data.get('message') else None,
            edited_message=Message.from_dict(data['edited_message']) if data.get('edited_message') else None,
            callback_query=CallbackQuery.from_dict(data['callback_query']) if data.get('callback_query') else None,
            inline_query=InlineQuery.from_dict(data['inline_query']) if data.get('inline_query') else None
        )
