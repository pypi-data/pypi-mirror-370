import re
import os
import mimetypes
import hashlib
import asyncio
from typing import Optional, List, Dict, Any, Union, Callable
from datetime import datetime, timedelta
import json


def validate_token(token: str) -> bool:
    if not token or not isinstance(token, str):
        return False
    pattern = r'^\d{8,10}:[a-zA-Z0-9_-]{35}$'
    return bool(re.match(pattern, token))


def format_text(text: str, **kwargs) -> str:
    try:
        return text.format(**kwargs)
    except KeyError:
        return text


def escape_markdown(text: str, version: int = 2) -> str:
    if version == 2:
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f'\\{char}')
    else:
        chars = ['_', '*', '[', '`']
        for char in chars:
            text = text.replace(char, f'\\{char}')
    return text


def escape_html(text: str) -> str:
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;'))


def parse_command(text: str) -> tuple:
    if not text or not text.startswith('/'):
        return None, []
    parts = text.split()
    command = parts[0][1:]
    args = parts[1:] if len(parts) > 1 else []
    return command, args


def get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def get_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'


def is_valid_chat_id(chat_id: Union[int, str]) -> bool:
    if isinstance(chat_id, int):
        return chat_id != 0
    elif isinstance(chat_id, str):
        return bool(chat_id.strip()) and (chat_id.startswith('@') or chat_id.lstrip('-').isdigit())
    return False


def generate_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def chunks(lst: List, n: int) -> List[List]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def persian_to_english_numbers(text: str) -> str:
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    for persian, english in zip(persian_digits, english_digits):
        text = text.replace(persian, english)
    return text


def english_to_persian_numbers(text: str) -> str:
    english_digits = '0123456789'
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    for english, persian in zip(english_digits, persian_digits):
        text = text.replace(english, persian)
    return text


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"


def get_username_from_url(url: str) -> Optional[str]:
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
    if not username:
        return False
    username = username.lstrip('@')
    if len(username) < 5 or len(username) > 32:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


def extract_user_id_from_mention(mention: str) -> Optional[int]:
    pattern = r'tg://user\?id=(\d+)'
    match = re.search(pattern, mention)
    if match:
        return int(match.group(1))
    return None


class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
        
    def is_allowed(self, key: str) -> bool:
        now = datetime.now()
        if key not in self.requests:
            self.requests[key] = []
        cutoff = now - timedelta(seconds=self.time_window)
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        if len(self.requests[key]) >= self.max_requests:
            return False
        self.requests[key].append(now)
        return True


class Cache:
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.data = {}
        
    def get(self, key: str) -> Any:
        if key in self.data:
            value, timestamp = self.data[key]
            if datetime.now().timestamp() - timestamp < self.ttl:
                return value
            else:
                del self.data[key]
        return None
        
    def set(self, key: str, value: Any):
        self.data[key] = (value, datetime.now().timestamp())
        
    def delete(self, key: str):
        if key in self.data:
            del self.data[key]
            
    def clear(self):
        self.data.clear()


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
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
                        await asyncio.sleep(delay * (2 ** attempt))
            raise last_exception
        return wrapper
    return decorator


def truncate_text(text: str, max_length: int = 4096, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def split_message(text: str, max_length: int = 4096) -> List[str]:
    if len(text) <= max_length:
        return [text]
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        split_point = text[:max_length].rfind(' ')
        if split_point == -1:
            split_point = max_length
        parts.append(text[:split_point])
        text = text[split_point:].lstrip()
    return parts


def create_quick_keyboard(*buttons) -> Dict[str, Any]:
    """Create inline keyboard quickly"""
    keyboard = {"inline_keyboard": []}
    row = []
    for i, button in enumerate(buttons):
        if isinstance(button, str):
            row.append({"text": button, "callback_data": button.lower().replace(" ", "_")})
        elif isinstance(button, tuple):
            text, data = button
            row.append({"text": text, "callback_data": data})
        
        if len(row) == 2 or i == len(buttons) - 1:
            keyboard["inline_keyboard"].append(row)
            row = []
    return keyboard


def create_contact_keyboard(text: str = "Share Contact") -> Dict[str, Any]:
    """Create contact sharing keyboard"""
    return {
        "keyboard": [[{"text": text, "request_contact": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


def create_location_keyboard(text: str = "Share Location") -> Dict[str, Any]:
    """Create location sharing keyboard"""
    return {
        "keyboard": [[{"text": text, "request_location": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


def create_poll_keyboard(*options) -> Dict[str, Any]:
    """Create poll-like keyboard"""
    keyboard = {"keyboard": []}
    for option in options:
        keyboard["keyboard"].append([{"text": f"📊 {option}"}])
    keyboard["resize_keyboard"] = True
    keyboard["one_time_keyboard"] = True
    return keyboard


def extract_command_args(text: str) -> tuple:
    """Extract command and arguments from message"""
    if not text or not text.startswith('/'):
        return None, []
    parts = text.split(maxsplit=1)
    command = parts[0][1:]
    args = parts[1] if len(parts) > 1 else ""
    return command, args


def format_user_mention(user_id: int, name: str) -> str:
    """Create user mention"""
    return f'<a href="tg://user?id={user_id}">{escape_html(name)}</a>'


def format_bold(text: str) -> str:
    """Format text as bold HTML"""
    return f"<b>{escape_html(text)}</b>"


def format_italic(text: str) -> str:
    """Format text as italic HTML"""
    return f"<i>{escape_html(text)}</i>"


def format_code(text: str) -> str:
    """Format text as code HTML"""
    return f"<code>{escape_html(text)}</code>"


def format_pre(text: str, language: str = "") -> str:
    """Format text as preformatted HTML"""
    lang_attr = f' class="language-{language}"' if language else ""
    return f"<pre{lang_attr}>{escape_html(text)}</pre>"


def format_link(text: str, url: str) -> str:
    """Create HTML link"""
    return f'<a href="{url}">{escape_html(text)}</a>'


def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create text progress bar"""
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    percentage = int(100 * current / total)
    return f"{bar} {percentage}%"


def format_time_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def smart_truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Smart text truncation"""
    if len(text) <= max_length:
        return text
    
    # Try to break at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length // 2:
        return truncated[:last_space] + suffix
    else:
        return truncated + suffix


def extract_urls_with_titles(text: str) -> List[Dict[str, str]]:
    """Extract URLs and their surrounding text"""
    import re
    url_pattern = r'(https?://\S+)'
    urls = []
    
    for match in re.finditer(url_pattern, text):
        url = match.group(1)
        start = max(0, match.start() - 20)
        end = min(len(text), match.end() + 20)
        context = text[start:end].strip()
        
        urls.append({
            "url": url,
            "context": context,
            "position": match.start()
        })
    
    return urls


def clean_telegram_formatting(text: str) -> str:
    """Remove Telegram formatting from text"""
    import re
    # Remove markdown
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'```([^`]+)```', r'\1', text)
    
    # Remove HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    return text.strip()


def generate_keyboard_from_list(items: List[str], columns: int = 2) -> Dict[str, Any]:
    """Generate keyboard from list of items"""
    keyboard = {"inline_keyboard": []}
    
    for i in range(0, len(items), columns):
        row = []
        for j in range(columns):
            if i + j < len(items):
                item = items[i + j]
                row.append({
                    "text": item,
                    "callback_data": f"item_{i + j}"
                })
        keyboard["inline_keyboard"].append(row)
    
    return keyboard


def create_numbered_list(items: List[str], start: int = 1) -> str:
    """Create numbered list string"""
    result = []
    for i, item in enumerate(items, start):
        result.append(f"{i}. {item}")
    return "\n".join(result)


def create_bulleted_list(items: List[str], bullet: str = "•") -> str:
    """Create bulleted list string"""
    return "\n".join(f"{bullet} {item}" for item in items)


def format_table(data: List[List[str]], headers: List[str] = None) -> str:
    """Format data as simple table"""
    if not data:
        return ""
    
    all_rows = [headers] + data if headers else data
    
    # Calculate column widths
    col_widths = []
    for col in range(len(all_rows[0])):
        max_width = max(len(str(row[col])) for row in all_rows)
        col_widths.append(max_width)
    
    # Format rows
    formatted_rows = []
    for i, row in enumerate(all_rows):
        formatted_row = " | ".join(
            str(cell).ljust(col_widths[j]) for j, cell in enumerate(row)
        )
        formatted_rows.append(formatted_row)
        
        # Add separator after header
        if i == 0 and headers:
            separator = "-+-".join("-" * width for width in col_widths)
            formatted_rows.append(separator)
    
    return "\n".join(formatted_rows)


def validate_telegram_username(username: str) -> bool:
    """Validate Telegram username format"""
    import re
    if not username:
        return False
    
    # Remove @ if present
    username = username.lstrip('@')
    
    # Check length and format
    return (
        5 <= len(username) <= 32 and
        re.match(r'^[a-zA-Z0-9_]+$', username) and
        not username.startswith('_') and
        not username.endswith('_')
    )


class MessageBuilder:
    """Build complex messages easily"""
    
    def __init__(self):
        self.parts = []
    
    def add_line(self, text: str = "") -> "MessageBuilder":
        self.parts.append(text)
        return self
        
    def add_bold(self, text: str) -> "MessageBuilder":
        self.parts.append(format_bold(text))
        return self
        
    def add_italic(self, text: str) -> "MessageBuilder":
        self.parts.append(format_italic(text))
        return self
        
    def add_code(self, text: str) -> "MessageBuilder":
        self.parts.append(format_code(text))
        return self
        
    def add_link(self, text: str, url: str) -> "MessageBuilder":
        self.parts.append(format_link(text, url))
        return self
        
    def add_mention(self, name: str, user_id: int) -> "MessageBuilder":
        self.parts.append(format_user_mention(user_id, name))
        return self
        
    def add_separator(self, char: str = "-", length: int = 20) -> "MessageBuilder":
        self.parts.append(char * length)
        return self
        
    def build(self, separator: str = "\n") -> str:
        return separator.join(str(part) for part in self.parts)


def create_status_message(status: str, details: Dict[str, Any]) -> str:
    """Create formatted status message"""
    builder = MessageBuilder()
    
    status_emoji = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "loading": "⏳"
    }
    
    emoji = status_emoji.get(status.lower(), "📋")
    builder.add_bold(f"{emoji} {status.upper()}")
    builder.add_line()
    
    for key, value in details.items():
        builder.add_line(f"{key}: {format_code(str(value))}")
    
    return builder.build()