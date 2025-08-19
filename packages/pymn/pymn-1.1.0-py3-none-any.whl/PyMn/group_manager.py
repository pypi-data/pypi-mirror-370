import asyncio
import json
import time
import logging
from typing import Optional, List, Dict, Any, Union, Callable
from .bot import Bot
from .types import Message, User, Chat
from .utils import MessageBuilder, format_user_mention


class GroupManager:
    """Advanced group management and moderation system"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.group_settings = {}
        self.user_warns = {}
        self.spam_tracker = {}
        self.flood_tracker = {}
        self.banned_words = {}
        self.auto_moderation = {}
        self.welcome_messages = {}
        self.admin_logs = {}
        
    def setup_group(self, chat_id: Union[int, str], settings: Dict[str, Any]) -> None:
        """Setup group with smart admin settings"""
        default_settings = {
            "anti_spam": True,
            "anti_flood": True,
            "max_warns": 3,
            "warn_action": "ban",
            "welcome_enabled": True,
            "auto_delete_commands": True,
            "max_messages_per_minute": 10,
            "banned_words_action": "warn",
            "link_protection": True,
            "media_restriction": False,
            "admin_only_pins": True,
            "auto_promote_trusted": False,
            "log_all_actions": True
        }
        
        default_settings.update(settings)
        self.group_settings[chat_id] = default_settings
        
        if chat_id not in self.user_warns:
            self.user_warns[chat_id] = {}
        if chat_id not in self.banned_words:
            self.banned_words[chat_id] = []
        if chat_id not in self.admin_logs:
            self.admin_logs[chat_id] = []
            
    async def check_message(self, message: Message) -> Dict[str, Any]:
        """Smart message checking with auto-moderation"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if chat_id not in self.group_settings:
            return {"action": "none", "reason": "group_not_configured"}
            
        settings = self.group_settings[chat_id]
        result = {"action": "none", "reason": "", "delete_message": False}
        
        if await self.bot.is_user_admin(chat_id, user_id):
            return result
            
        if settings.get("anti_spam") and await self._check_spam(message):
            result["action"] = "spam_detected"
            result["delete_message"] = True
            await self._handle_spam_user(message)
            
        elif settings.get("anti_flood") and await self._check_flood(message):
            result["action"] = "flood_detected" 
            result["delete_message"] = True
            await self._handle_flood_user(message)
            
        elif settings.get("banned_words") and await self._check_banned_words(message):
            result["action"] = "banned_word"
            result["delete_message"] = True
            await self._handle_banned_word(message)
            
        elif settings.get("link_protection") and await self._check_links(message):
            result["action"] = "unauthorized_link"
            result["delete_message"] = True
            await self._handle_unauthorized_link(message)
            
        if result["delete_message"]:
            await self.bot.delete_message(chat_id, message.message_id)
            
        return result
        
    async def _check_spam(self, message: Message) -> bool:
        """Advanced spam detection"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text or message.caption or ""
        
        spam_indicators = 0
        
        if len(text) > 1000:
            spam_indicators += 2
            
        if text.count("http") > 2:
            spam_indicators += 3
            
        if len(set(text)) / len(text) < 0.3 and len(text) > 50:
            spam_indicators += 2
            
        emoji_count = sum(1 for char in text if ord(char) > 0x1F600)
        if emoji_count > len(text) * 0.3:
            spam_indicators += 2
            
        repeated_chars = max(len([c for c in text if c == char]) for char in set(text)) if text else 0
        if repeated_chars > 10:
            spam_indicators += 2
            
        if user_id not in self.spam_tracker:
            self.spam_tracker[user_id] = {"score": 0, "last_reset": time.time()}
            
        current_time = time.time()
        if current_time - self.spam_tracker[user_id]["last_reset"] > 3600:
            self.spam_tracker[user_id]["score"] = 0
            self.spam_tracker[user_id]["last_reset"] = current_time
            
        self.spam_tracker[user_id]["score"] += spam_indicators
        
        return self.spam_tracker[user_id]["score"] > 5
        
    async def _check_flood(self, message: Message) -> bool:
        """Advanced flood detection"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        current_time = time.time()
        
        if user_id not in self.flood_tracker:
            self.flood_tracker[user_id] = []
            
        self.flood_tracker[user_id] = [
            msg_time for msg_time in self.flood_tracker[user_id] 
            if current_time - msg_time < 60
        ]
        
        self.flood_tracker[user_id].append(current_time)
        
        max_messages = self.group_settings[chat_id].get("max_messages_per_minute", 10)
        return len(self.flood_tracker[user_id]) > max_messages
        
    async def _check_banned_words(self, message: Message) -> bool:
        """Check for banned words"""
        chat_id = message.chat.id
        text = (message.text or message.caption or "").lower()
        
        banned_words = self.banned_words.get(chat_id, [])
        return any(word.lower() in text for word in banned_words)
        
    async def _check_links(self, message: Message) -> bool:
        """Check for unauthorized links"""
        text = message.text or message.caption or ""
        link_patterns = ["http://", "https://", "t.me/", "@", "telegram.me/"]
        return any(pattern in text.lower() for pattern in link_patterns)
        
    async def _handle_spam_user(self, message: Message) -> None:
        """Handle spam user"""
        await self._warn_user(message, "Spam detected")
        
    async def _handle_flood_user(self, message: Message) -> None:
        """Handle flood user"""
        await self._mute_user_temporarily(message, 300)
        
    async def _handle_banned_word(self, message: Message) -> None:
        """Handle banned word usage"""
        action = self.group_settings[message.chat.id].get("banned_words_action", "warn")
        
        if action == "warn":
            await self._warn_user(message, "Used banned word")
        elif action == "mute":
            await self._mute_user_temporarily(message, 600)
        elif action == "ban":
            await self.bot.safe_ban_user(message.chat.id, message.from_user.id)
            
    async def _handle_unauthorized_link(self, message: Message) -> None:
        """Handle unauthorized link"""
        await self._warn_user(message, "Unauthorized link")
        
    async def _warn_user(self, message: Message, reason: str) -> None:
        """Smart warn system"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if chat_id not in self.user_warns:
            self.user_warns[chat_id] = {}
            
        if user_id not in self.user_warns[chat_id]:
            self.user_warns[chat_id][user_id] = []
            
        warn_data = {
            "reason": reason,
            "timestamp": time.time(),
            "message_id": message.message_id
        }
        
        self.user_warns[chat_id][user_id].append(warn_data)
        warn_count = len(self.user_warns[chat_id][user_id])
        max_warns = self.group_settings[chat_id].get("max_warns", 3)
        
        builder = MessageBuilder()
        builder.add_bold(f"⚠️ Warning {warn_count}/{max_warns}")
        builder.add_line()
        builder.add_line(f"User: {format_user_mention(user_id, message.from_user.first_name)}")
        builder.add_line(f"Reason: {reason}")
        
        if warn_count >= max_warns:
            action = self.group_settings[chat_id].get("warn_action", "ban")
            
            if action == "ban":
                await self.bot.safe_ban_user(chat_id, user_id)
                builder.add_line("Action: Banned")
            elif action == "kick":
                await self.bot.safe_kick_user(chat_id, user_id)
                builder.add_line("Action: Kicked")
            elif action == "mute":
                await self.bot.mute_user_safely(chat_id, user_id)
                builder.add_line("Action: Muted")
                
            self.user_warns[chat_id][user_id] = []
        else:
            builder.add_line(f"Next warning will result in {self.group_settings[chat_id].get('warn_action', 'ban')}")
            
        await self.bot.send_temp_message(chat_id, builder.build(), delete_after=30)
        
    async def _mute_user_temporarily(self, message: Message, duration: int) -> None:
        """Mute user temporarily"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        await self.bot.mute_user_safely(chat_id, user_id, until_date=int(time.time() + duration))
        
        builder = MessageBuilder()
        builder.add_bold("🔇 User Temporarily Muted")
        builder.add_line()
        builder.add_line(f"User: {format_user_mention(user_id, message.from_user.first_name)}")
        builder.add_line(f"Duration: {duration // 60} minutes")
        
        await self.bot.send_temp_message(chat_id, builder.build(), delete_after=20)
        
    async def add_banned_word(self, chat_id: Union[int, str], word: str) -> bool:
        """Add banned word"""
        if chat_id not in self.banned_words:
            self.banned_words[chat_id] = []
            
        if word.lower() not in [w.lower() for w in self.banned_words[chat_id]]:
            self.banned_words[chat_id].append(word)
            return True
        return False
        
    async def remove_banned_word(self, chat_id: Union[int, str], word: str) -> bool:
        """Remove banned word"""
        if chat_id in self.banned_words:
            original_length = len(self.banned_words[chat_id])
            self.banned_words[chat_id] = [w for w in self.banned_words[chat_id] if w.lower() != word.lower()]
            return len(self.banned_words[chat_id]) < original_length
        return False
        
    async def get_user_warnings(self, chat_id: Union[int, str], user_id: int) -> List[Dict]:
        """Get user warnings"""
        return self.user_warns.get(chat_id, {}).get(user_id, [])
        
    async def clear_user_warnings(self, chat_id: Union[int, str], user_id: int) -> bool:
        """Clear user warnings"""
        if chat_id in self.user_warns and user_id in self.user_warns[chat_id]:
            self.user_warns[chat_id][user_id] = []
            return True
        return False
        
    async def set_welcome_message(self, chat_id: Union[int, str], message: str) -> None:
        """Set welcome message"""
        self.welcome_messages[chat_id] = message
        
    async def send_welcome(self, chat_id: Union[int, str], new_user: User) -> None:
        """Send welcome message"""
        if chat_id not in self.welcome_messages:
            return
            
        welcome_text = self.welcome_messages[chat_id]
        welcome_text = welcome_text.replace("{user}", format_user_mention(new_user.id, new_user.first_name))
        welcome_text = welcome_text.replace("{chat}", f"@{chat_id}" if isinstance(chat_id, str) else str(chat_id))
        
        await self.bot.send_message(chat_id, welcome_text)
        
    async def log_admin_action(self, chat_id: Union[int, str], admin_id: int, action: str, details: Dict) -> None:
        """Log admin actions"""
        if chat_id not in self.admin_logs:
            self.admin_logs[chat_id] = []
            
        log_entry = {
            "admin_id": admin_id,
            "action": action,
            "details": details,
            "timestamp": time.time()
        }
        
        self.admin_logs[chat_id].append(log_entry)
        
        if len(self.admin_logs[chat_id]) > 1000:
            self.admin_logs[chat_id] = self.admin_logs[chat_id][-500:]
            
    async def get_group_stats(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        """Get comprehensive group statistics"""
        stats = {
            "total_warnings": sum(len(warns) for warns in self.user_warns.get(chat_id, {}).values()),
            "banned_words_count": len(self.banned_words.get(chat_id, [])),
            "admin_actions": len(self.admin_logs.get(chat_id, [])),
            "active_users": len(self.user_warns.get(chat_id, {})),
            "spam_detections": sum(1 for user_id, data in self.spam_tracker.items() if data["score"] > 0),
            "flood_violations": len([user_id for user_id, times in self.flood_tracker.items() if len(times) > 5])
        }
        
        return stats
        
    async def export_group_data(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        """Export all group data"""
        return {
            "settings": self.group_settings.get(chat_id, {}),
            "warnings": self.user_warns.get(chat_id, {}),
            "banned_words": self.banned_words.get(chat_id, []),
            "welcome_message": self.welcome_messages.get(chat_id, ""),
            "admin_logs": self.admin_logs.get(chat_id, []),
            "stats": await self.get_group_stats(chat_id)
        }
        
    async def import_group_data(self, chat_id: Union[int, str], data: Dict[str, Any]) -> bool:
        """Import group data"""
        try:
            if "settings" in data:
                self.group_settings[chat_id] = data["settings"]
            if "warnings" in data:
                self.user_warns[chat_id] = data["warnings"]
            if "banned_words" in data:
                self.banned_words[chat_id] = data["banned_words"]
            if "welcome_message" in data:
                self.welcome_messages[chat_id] = data["welcome_message"]
            if "admin_logs" in data:
                self.admin_logs[chat_id] = data["admin_logs"]
                
            return True
        except Exception as e:
            logging.error(f"Failed to import group data: {e}")
            return False
