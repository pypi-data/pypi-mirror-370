import asyncio
import aiohttp
import json
import logging
import hashlib
import hmac
import time
from typing import Optional, Callable, List, Dict, Any, Union
from .types import Update, Message, CallbackQuery, User, Chat
from .exceptions import BotException, APIException, NetworkException
from .utils import validate_token, format_text


class UserBot:
    """Advanced UserBot for Telegram with API ID/Hash support"""
    
    def __init__(self, api_id: int, api_hash: str, phone_number: str, session_string: Optional[str] = None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_string = session_string
        self.session = None
        self.running = False
        self.handlers = {
            'message': [],
            'edited_message': [],
            'channel_post': [],
            'callback_query': [],
            'inline_query': []
        }
        self.user_info = None
        self.rate_limits = {}
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def _make_request(self, method: str, data: Dict[str, Any]) -> Any:
        """Make MTProto request with rate limiting"""
        current_time = time.time()
        
        if method in self.rate_limits:
            time_diff = current_time - self.rate_limits[method]
            if time_diff < 1.0:
                await asyncio.sleep(1.0 - time_diff)
        
        self.rate_limits[method] = time.time()
        
        session = await self._get_session()
        url = f"https://api.telegram.org/mt/{method}"
        
        try:
            async with session.post(url, json=data) as response:
                result = await response.json()
                
                if not result.get('ok'):
                    error_code = result.get('error_code', 0)
                    description = result.get('description', 'Unknown error')
                    
                    if error_code == 429:
                        retry_after = result.get('parameters', {}).get('retry_after', 60)
                        await asyncio.sleep(retry_after)
                        return await self._make_request(method, data)
                    elif error_code >= 500:
                        raise NetworkException(f"Server error: {description}")
                    else:
                        raise APIException(f"API error {error_code}: {description}")
                
                return result.get('result')
                
        except aiohttp.ClientError as e:
            raise NetworkException(f"Network error: {str(e)}")
        except Exception as e:
            raise BotException(f"Request failed: {str(e)}")
            
    async def connect(self) -> bool:
        """Connect to Telegram using MTProto"""
        try:
            data = {
                "api_id": self.api_id,
                "api_hash": self.api_hash,
                "phone_number": self.phone_number
            }
            
            if self.session_string:
                data["session"] = self.session_string
                
            result = await self._make_request("auth.signIn", data)
            self.user_info = result.get('user')
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return False
            
    async def send_message_as_user(self, chat_id: Union[int, str], text: str,
                                  reply_to_message_id: Optional[int] = None,
                                  parse_mode: str = "HTML") -> Optional[Message]:
        """Send message as user (no bot restrictions)"""
        try:
            data = {
                "peer": chat_id,
                "message": text,
                "parse_mode": parse_mode
            }
            
            if reply_to_message_id:
                data["reply_to_msg_id"] = reply_to_message_id
                
            result = await self._make_request("messages.sendMessage", data)
            return Message.from_dict(result) if result else None
            
        except Exception as e:
            logging.error(f"Failed to send user message: {e}")
            return None
            
    async def forward_message_as_user(self, to_chat_id: Union[int, str], from_chat_id: Union[int, str],
                                     message_id: int, silent: bool = False) -> Optional[Message]:
        """Forward message as user"""
        try:
            data = {
                "to_peer": to_chat_id,
                "from_peer": from_chat_id,
                "id": [message_id],
                "silent": silent
            }
            
            result = await self._make_request("messages.forwardMessages", data)
            return Message.from_dict(result[0]) if result else None
            
        except Exception as e:
            logging.error(f"Failed to forward message: {e}")
            return None
            
    async def delete_message_as_user(self, chat_id: Union[int, str], message_id: int,
                                    revoke: bool = True) -> bool:
        """Delete message as user"""
        try:
            data = {
                "peer": chat_id,
                "id": [message_id],
                "revoke": revoke
            }
            
            await self._make_request("messages.deleteMessages", data)
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete message: {e}")
            return False
            
    async def edit_message_as_user(self, chat_id: Union[int, str], message_id: int,
                                  text: str, parse_mode: str = "HTML") -> Optional[Message]:
        """Edit message as user"""
        try:
            data = {
                "peer": chat_id,
                "id": message_id,
                "message": text,
                "parse_mode": parse_mode
            }
            
            result = await self._make_request("messages.editMessage", data)
            return Message.from_dict(result) if result else None
            
        except Exception as e:
            logging.error(f"Failed to edit message: {e}")
            return None
            
    async def join_chat_as_user(self, chat_link: str) -> bool:
        """Join chat/channel as user"""
        try:
            data = {"hash": chat_link.split('/')[-1]}
            await self._make_request("messages.importChatInvite", data)
            return True
            
        except Exception as e:
            logging.error(f"Failed to join chat: {e}")
            return False
            
    async def leave_chat_as_user(self, chat_id: Union[int, str]) -> bool:
        """Leave chat as user"""
        try:
            data = {"peer": chat_id}
            await self._make_request("channels.leaveChannel", data)
            return True
            
        except Exception as e:
            logging.error(f"Failed to leave chat: {e}")
            return False
            
    async def get_chat_members_as_user(self, chat_id: Union[int, str], limit: int = 100) -> List[dict]:
        """Get chat members as user (bypass restrictions)"""
        try:
            data = {
                "channel": chat_id,
                "filter": {"_": "channelParticipantsRecent"},
                "offset": 0,
                "limit": limit,
                "hash": 0
            }
            
            result = await self._make_request("channels.getParticipants", data)
            return result.get('participants', [])
            
        except Exception as e:
            logging.error(f"Failed to get chat members: {e}")
            return []
            
    async def read_chat_history(self, chat_id: Union[int, str], limit: int = 100) -> List[Message]:
        """Read chat history as user"""
        try:
            data = {
                "peer": chat_id,
                "offset_id": 0,
                "offset_date": 0,
                "add_offset": 0,
                "limit": limit,
                "max_id": 0,
                "min_id": 0,
                "hash": 0
            }
            
            result = await self._make_request("messages.getHistory", data)
            messages = result.get('messages', [])
            return [Message.from_dict(msg) for msg in messages]
            
        except Exception as e:
            logging.error(f"Failed to read chat history: {e}")
            return []
            
    async def search_global_messages(self, query: str, limit: int = 50) -> List[Message]:
        """Search global messages as user"""
        try:
            data = {
                "q": query,
                "filter": {"_": "inputMessagesFilterEmpty"},
                "min_date": 0,
                "max_date": 0,
                "offset_id": 0,
                "add_offset": 0,
                "limit": limit,
                "max_id": 0,
                "min_id": 0,
                "hash": 0
            }
            
            result = await self._make_request("messages.searchGlobal", data)
            messages = result.get('messages', [])
            return [Message.from_dict(msg) for msg in messages]
            
        except Exception as e:
            logging.error(f"Failed to search messages: {e}")
            return []
            
    async def get_user_info_detailed(self, user_id: int) -> Optional[dict]:
        """Get detailed user info as user"""
        try:
            data = {"id": [{"_": "inputUser", "user_id": user_id, "access_hash": 0}]}
            result = await self._make_request("users.getUsers", data)
            return result[0] if result else None
            
        except Exception as e:
            logging.error(f"Failed to get user info: {e}")
            return None
            
    async def mass_message_users(self, user_ids: List[int], text: str, delay: int = 2) -> Dict[int, bool]:
        """Send message to multiple users with delay"""
        results = {}
        
        for user_id in user_ids:
            try:
                message = await self.send_message_as_user(user_id, text)
                results[user_id] = message is not None
                await asyncio.sleep(delay)
                
            except Exception as e:
                logging.error(f"Failed to send to {user_id}: {e}")
                results[user_id] = False
                
        return results
        
    async def auto_react_to_messages(self, chat_id: Union[int, str], emoji: str = "👍",
                                    interval: int = 60) -> None:
        """Auto react to new messages"""
        last_message_id = 0
        
        while self.running:
            try:
                messages = await self.read_chat_history(chat_id, limit=10)
                
                for message in messages:
                    if message.message_id > last_message_id:
                        await self.react_to_message(chat_id, message.message_id, emoji)
                        last_message_id = message.message_id
                        
                await asyncio.sleep(interval)
                
            except Exception as e:
                logging.error(f"Auto react error: {e}")
                await asyncio.sleep(interval)
                
    async def react_to_message(self, chat_id: Union[int, str], message_id: int, emoji: str) -> bool:
        """React to message as user"""
        try:
            data = {
                "peer": chat_id,
                "msg_id": message_id,
                "reaction": [{"_": "reactionEmoji", "emoticon": emoji}]
            }
            
            await self._make_request("messages.sendReaction", data)
            return True
            
        except Exception as e:
            logging.error(f"Failed to react: {e}")
            return False
            
    async def create_secret_chat(self, user_id: int) -> Optional[dict]:
        """Create secret chat as user"""
        try:
            data = {
                "user_id": user_id,
                "random_id": int(time.time())
            }
            
            result = await self._make_request("messages.requestEncryption", data)
            return result
            
        except Exception as e:
            logging.error(f"Failed to create secret chat: {e}")
            return None
            
    async def close(self) -> None:
        """Close userbot session"""
        self.running = False
        if self.session and not self.session.closed:
            await self.session.close()
            
    def run_userbot(self) -> None:
        """Run userbot"""
        self.running = True
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        loop.run_until_complete(self._run_polling())
        
    async def _run_polling(self) -> None:
        """Internal polling method"""
        while self.running:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(f"Polling error: {e}")
                await asyncio.sleep(5)
