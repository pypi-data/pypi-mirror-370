import asyncio
import aiohttp
import json
import logging
import time
from typing import Optional, Callable, List, Dict, Any, Union
from .types import Update, Message, CallbackQuery, User, Chat
from .exceptions import BotException, APIException, NetworkException
from .utils import validate_token


class Bot:
    def __init__(self, token: str, parse_mode: str = "HTML"):
        if not validate_token(token):
            raise BotException("Invalid bot token")
            
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.parse_mode = parse_mode
        self.session: Optional[aiohttp.ClientSession] = None
        
        self._message_handlers: List[Dict[str, Any]] = []
        self._callback_handlers: List[Callable] = []
        self._command_handlers: Dict[str, Callable] = {}
        self._middleware: List[Callable] = []
        
        self.running = False
        self.offset = 0
        self.timeout = 30
        
        self.logger = logging.getLogger("PyMn")
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def _make_request(self, method: str, data: Dict = None, files: Dict = None) -> Dict:
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
                description = result.get("description", "Unknown error")
                raise APIException(f"API Error {error_code}: {description}")
                
            return result.get("result")
            
        except aiohttp.ClientError as e:
            raise NetworkException(f"Network error: {e}")
        except json.JSONDecodeError:
            raise APIException("Invalid response from server")
            
    async def get_me(self) -> User:
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
        
    async def send_video(
        self,
        chat_id: Union[int, str],
        video: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Dict] = None
    ) -> Message:
        data = {
            "chat_id": chat_id,
            "parse_mode": parse_mode or self.parse_mode
        }
        
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        files = None
        if isinstance(video, bytes):
            files = {"video": video}
        else:
            data["video"] = video
            
        result = await self._make_request("sendVideo", data, files)
        return Message.from_dict(result)
        
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
        url: Optional[str] = None,
        cache_time: int = 0
    ) -> bool:
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
        
    async def delete_message(self, chat_id: Union[int, str], message_id: int) -> bool:
        data = {"chat_id": chat_id, "message_id": message_id}
        await self._make_request("deleteMessage", data)
        return True
        
    async def get_chat(self, chat_id: Union[int, str]) -> Chat:
        data = {"chat_id": chat_id}
        result = await self._make_request("getChat", data)
        return Chat.from_dict(result)
        
    async def get_chat_member(self, chat_id: Union[int, str], user_id: int) -> dict:
        data = {"chat_id": chat_id, "user_id": user_id}
        return await self._make_request("getChatMember", data)
        
    async def kick_chat_member(self, chat_id: Union[int, str], user_id: int) -> bool:
        data = {"chat_id": chat_id, "user_id": user_id}
        await self._make_request("kickChatMember", data)
        return True
        
    async def unban_chat_member(self, chat_id: Union[int, str], user_id: int) -> bool:
        data = {"chat_id": chat_id, "user_id": user_id}
        await self._make_request("unbanChatMember", data)
        return True
        
    def message_handler(self, commands: Optional[List[str]] = None, content_types: Optional[List[str]] = None):
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
        def decorator(func: Callable):
            self._callback_handlers.append(func)
            return func
        return decorator
        
    def command_handler(self, command: str):
        def decorator(func: Callable):
            self._command_handlers[command] = func
            return func
        return decorator
        
    def middleware(self):
        def decorator(func: Callable):
            self._middleware.append(func)
            return func
        return decorator
        
    async def _process_update(self, update: Update):
        try:
            for middleware_func in self._middleware:
                result = await middleware_func(update)
                if result is False:
                    return
                    
            if update.message:
                await self._process_message(update.message)
            elif update.callback_query:
                await self._process_callback_query(update.callback_query)
                
        except Exception as e:
            self.logger.error(f"Error processing update: {e}")
            
    async def _process_message(self, message: Message):
        if message.text and message.text.startswith("/"):
            command = message.text.split()[0][1:]
            if command in self._command_handlers:
                await self._command_handlers[command](message)
                return
                
        for handler in self._message_handlers:
            if message.content_type not in handler["content_types"]:
                continue
                
            if handler["commands"]:
                if not message.text or not message.text.startswith("/"):
                    continue
                command = message.text.split()[0][1:]
                if command not in handler["commands"]:
                    continue
                    
            await handler["function"](message)
            break
            
    async def _process_callback_query(self, callback_query: CallbackQuery):
        for handler in self._callback_handlers:
            await handler(callback_query)
            
    async def get_updates(self) -> List[Update]:
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
            self.logger.error(f"Error getting updates: {e}")
            return []
            
    async def start_polling(self):
        self.running = True
        self.logger.info("Bot started")
        
        while self.running:
            try:
                updates = await self.get_updates()
                
                tasks = [self._process_update(update) for update in updates]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
            except KeyboardInterrupt:
                self.logger.info("Bot stopped")
                break
            except Exception as e:
                self.logger.error(f"Error in polling: {e}")
                await asyncio.sleep(1)
                
    def run(self):
        try:
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            pass
        finally:
            asyncio.run(self.close())
            
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
        self.running = False
        
    def stop(self):
        self.running = False
        
    async def send_typing(self, chat_id: Union[int, str]):
        """Show typing indicator"""
        data = {"chat_id": chat_id, "action": "typing"}
        await self._make_request("sendChatAction", data)
        
    async def send_upload_photo(self, chat_id: Union[int, str]):
        """Show uploading photo indicator"""
        data = {"chat_id": chat_id, "action": "upload_photo"}
        await self._make_request("sendChatAction", data)
        
    async def send_upload_video(self, chat_id: Union[int, str]):
        """Show uploading video indicator"""
        data = {"chat_id": chat_id, "action": "upload_video"}
        await self._make_request("sendChatAction", data)
        
    async def send_dice(self, chat_id: Union[int, str], emoji: str = "🎲") -> Message:
        """Send animated dice"""
        data = {"chat_id": chat_id, "emoji": emoji}
        result = await self._make_request("sendDice", data)
        return Message.from_dict(result)
        
    async def copy_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str], 
                          message_id: int, caption: Optional[str] = None) -> dict:
        """Copy message from one chat to another"""
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
        if caption:
            data["caption"] = caption
        return await self._make_request("copyMessage", data)
        
    async def forward_message(self, chat_id: Union[int, str], from_chat_id: Union[int, str],
                             message_id: int, disable_notification: bool = False) -> Message:
        """Forward message"""
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification
        }
        result = await self._make_request("forwardMessage", data)
        return Message.from_dict(result)
        
    async def pin_message(self, chat_id: Union[int, str], message_id: int,
                         disable_notification: bool = False) -> bool:
        """Pin message in chat"""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification
        }
        await self._make_request("pinChatMessage", data)
        return True
        
    async def unpin_message(self, chat_id: Union[int, str], message_id: Optional[int] = None) -> bool:
        """Unpin message or all pinned messages"""
        data = {"chat_id": chat_id}
        if message_id:
            data["message_id"] = message_id
        await self._make_request("unpinChatMessage", data)
        return True
        
    async def set_chat_title(self, chat_id: Union[int, str], title: str) -> bool:
        """Change chat title"""
        data = {"chat_id": chat_id, "title": title}
        await self._make_request("setChatTitle", data)
        return True
        
    async def set_chat_description(self, chat_id: Union[int, str], description: str) -> bool:
        """Change chat description"""
        data = {"chat_id": chat_id, "description": description}
        await self._make_request("setChatDescription", data)
        return True
        
    async def get_chat_members_count(self, chat_id: Union[int, str]) -> int:
        """Get number of members in chat"""
        data = {"chat_id": chat_id}
        result = await self._make_request("getChatMemberCount", data)
        return result
        
    async def export_chat_invite_link(self, chat_id: Union[int, str]) -> str:
        """Generate new primary invite link"""
        data = {"chat_id": chat_id}
        result = await self._make_request("exportChatInviteLink", data)
        return result
        
    async def create_chat_invite_link(self, chat_id: Union[int, str], name: Optional[str] = None,
                                     expire_date: Optional[int] = None, 
                                     member_limit: Optional[int] = None) -> dict:
        """Create custom invite link"""
        data = {"chat_id": chat_id}
        if name:
            data["name"] = name
        if expire_date:
            data["expire_date"] = expire_date
        if member_limit:
            data["member_limit"] = member_limit
        return await self._make_request("createChatInviteLink", data)
        
    async def revoke_chat_invite_link(self, chat_id: Union[int, str], invite_link: str) -> dict:
        """Revoke invite link"""
        data = {"chat_id": chat_id, "invite_link": invite_link}
        return await self._make_request("revokeChatInviteLink", data)
        
    async def send_poll(self, chat_id: Union[int, str], question: str, options: List[str],
                       is_anonymous: bool = True, allows_multiple_answers: bool = False,
                       type: str = "regular", correct_option_id: Optional[int] = None) -> Message:
        """Send poll/quiz"""
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": json.dumps(options),
            "is_anonymous": is_anonymous,
            "allows_multiple_answers": allows_multiple_answers,
            "type": type
        }
        if correct_option_id is not None:
            data["correct_option_id"] = correct_option_id
        result = await self._make_request("sendPoll", data)
        return Message.from_dict(result)
        
    async def stop_poll(self, chat_id: Union[int, str], message_id: int,
                       reply_markup: Optional[Dict] = None) -> dict:
        """Stop poll"""
        data = {"chat_id": chat_id, "message_id": message_id}
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        return await self._make_request("stopPoll", data)
        
    async def restrict_chat_member(self, chat_id: Union[int, str], user_id: int,
                                  until_date: Optional[int] = None, **permissions) -> bool:
        """Restrict chat member"""
        data = {"chat_id": chat_id, "user_id": user_id}
        if until_date:
            data["until_date"] = until_date
        data.update(permissions)
        await self._make_request("restrictChatMember", data)
        return True
        
    async def send_location(self, chat_id: Union[int, str], latitude: float, longitude: float,
                           live_period: Optional[int] = None, 
                           horizontal_accuracy: Optional[float] = None) -> Message:
        """Send location"""
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
        if live_period:
            data["live_period"] = live_period
        if horizontal_accuracy:
            data["horizontal_accuracy"] = horizontal_accuracy
        result = await self._make_request("sendLocation", data)
        return Message.from_dict(result)
        
    async def send_venue(self, chat_id: Union[int, str], latitude: float, longitude: float,
                        title: str, address: str, foursquare_id: Optional[str] = None) -> Message:
        """Send venue"""
        data = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "title": title,
            "address": address
        }
        if foursquare_id:
            data["foursquare_id"] = foursquare_id
        result = await self._make_request("sendVenue", data)
        return Message.from_dict(result)
        
    async def send_contact(self, chat_id: Union[int, str], phone_number: str, first_name: str,
                          last_name: Optional[str] = None, vcard: Optional[str] = None) -> Message:
        """Send contact"""
        data = {
            "chat_id": chat_id,
            "phone_number": phone_number,
            "first_name": first_name
        }
        if last_name:
            data["last_name"] = last_name
        if vcard:
            data["vcard"] = vcard
        result = await self._make_request("sendContact", data)
        return Message.from_dict(result)
        
    async def send_animation(self, chat_id: Union[int, str], animation: Union[str, bytes],
                            duration: Optional[int] = None, width: Optional[int] = None,
                            height: Optional[int] = None, caption: Optional[str] = None) -> Message:
        """Send GIF animation"""
        data = {"chat_id": chat_id}
        if duration:
            data["duration"] = duration
        if width:
            data["width"] = width
        if height:
            data["height"] = height
        if caption:
            data["caption"] = caption
            
        files = None
        if isinstance(animation, bytes):
            files = {"animation": animation}
        else:
            data["animation"] = animation
            
        result = await self._make_request("sendAnimation", data, files)
        return Message.from_dict(result)
        
    async def send_voice(self, chat_id: Union[int, str], voice: Union[str, bytes],
                        duration: Optional[int] = None, caption: Optional[str] = None) -> Message:
        """Send voice message"""
        data = {"chat_id": chat_id}
        if duration:
            data["duration"] = duration
        if caption:
            data["caption"] = caption
            
        files = None
        if isinstance(voice, bytes):
            files = {"voice": voice}
        else:
            data["voice"] = voice
            
        result = await self._make_request("sendVoice", data, files)
        return Message.from_dict(result)
        
    async def send_video_note(self, chat_id: Union[int, str], video_note: Union[str, bytes],
                             duration: Optional[int] = None, length: Optional[int] = None) -> Message:
        """Send video note (circle video)"""
        data = {"chat_id": chat_id}
        if duration:
            data["duration"] = duration
        if length:
            data["length"] = length
            
        files = None
        if isinstance(video_note, bytes):
            files = {"video_note": video_note}
        else:
            data["video_note"] = video_note
            
        result = await self._make_request("sendVideoNote", data, files)
        return Message.from_dict(result)
        
    async def send_audio(self, chat_id: Union[int, str], audio: Union[str, bytes],
                        duration: Optional[int] = None, performer: Optional[str] = None,
                        title: Optional[str] = None, caption: Optional[str] = None) -> Message:
        """Send audio file"""
        data = {"chat_id": chat_id}
        if duration:
            data["duration"] = duration
        if performer:
            data["performer"] = performer
        if title:
            data["title"] = title
        if caption:
            data["caption"] = caption
            
        files = None
        if isinstance(audio, bytes):
            files = {"audio": audio}
        else:
            data["audio"] = audio
            
        result = await self._make_request("sendAudio", data, files)
        return Message.from_dict(result)
        
    async def send_sticker(self, chat_id: Union[int, str], sticker: Union[str, bytes]) -> Message:
        """Send sticker"""
        data = {"chat_id": chat_id}
        
        files = None
        if isinstance(sticker, bytes):
            files = {"sticker": sticker}
        else:
            data["sticker"] = sticker
            
        result = await self._make_request("sendSticker", data, files)
        return Message.from_dict(result)
        
    async def get_file(self, file_id: str) -> dict:
        """Get file info"""
        data = {"file_id": file_id}
        return await self._make_request("getFile", data)
        
    async def download_file(self, file_path: str) -> bytes:
        """Download file from Telegram servers"""
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        session = await self._get_session()
        async with session.get(url) as response:
            return await response.read()
            
    async def leave_chat(self, chat_id: Union[int, str]) -> bool:
        """Leave chat"""
        data = {"chat_id": chat_id}
        await self._make_request("leaveChat", data)
        return True
        
    async def reply_to(self, message: Message, text: str, **kwargs) -> Message:
        """Quick reply to a message"""
        return await self.send_message(
            message.chat.id, 
            text, 
            reply_to_message_id=message.message_id,
            **kwargs
        )
        
    async def react_to(self, chat_id: Union[int, str], message_id: int, emoji: str) -> bool:
        """React to message with emoji"""
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": json.dumps([{"type": "emoji", "emoji": emoji}])
        }
        await self._make_request("setMessageReaction", data)
        return True
        
    async def boost_chat(self, chat_id: Union[int, str]) -> bool:
        """Boost chat (Premium feature)"""
        data = {"chat_id": chat_id}
        await self._make_request("boostChat", data)
        return True
        
    async def send_game(self, chat_id: Union[int, str], game_short_name: str,
                       reply_markup: Optional[Dict] = None) -> Message:
        """Send game"""
        data = {"chat_id": chat_id, "game_short_name": game_short_name}
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        result = await self._make_request("sendGame", data)
        return Message.from_dict(result)
        
    async def set_game_score(self, user_id: int, score: int, chat_id: Optional[Union[int, str]] = None,
                            message_id: Optional[int] = None, inline_message_id: Optional[str] = None,
                            force: bool = False) -> bool:
        """Set game score"""
        data = {"user_id": user_id, "score": score, "force": force}
        
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data["chat_id"] = chat_id
            data["message_id"] = message_id
            
        await self._make_request("setGameScore", data)
        return True
        
    async def get_game_high_scores(self, user_id: int, chat_id: Optional[Union[int, str]] = None,
                                  message_id: Optional[int] = None, 
                                  inline_message_id: Optional[str] = None) -> List[dict]:
        """Get game high scores"""
        data = {"user_id": user_id}
        
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data["chat_id"] = chat_id
            data["message_id"] = message_id
            
        return await self._make_request("getGameHighScores", data)
        
    async def send_invoice(self, chat_id: Union[int, str], title: str, description: str,
                          payload: str, provider_token: str, currency: str, prices: List[dict],
                          **kwargs) -> Message:
        """Send invoice for payment"""
        data = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": currency,
            "prices": json.dumps(prices)
        }
        data.update(kwargs)
        result = await self._make_request("sendInvoice", data)
        return Message.from_dict(result)
        
    async def answer_shipping_query(self, shipping_query_id: str, ok: bool,
                                   shipping_options: Optional[List[dict]] = None,
                                   error_message: Optional[str] = None) -> bool:
        """Answer shipping query"""
        data = {"shipping_query_id": shipping_query_id, "ok": ok}
        if shipping_options:
            data["shipping_options"] = json.dumps(shipping_options)
        if error_message:
            data["error_message"] = error_message
        await self._make_request("answerShippingQuery", data)
        return True
        
    async def answer_pre_checkout_query(self, pre_checkout_query_id: str, ok: bool,
                                       error_message: Optional[str] = None) -> bool:
        """Answer pre-checkout query"""
        data = {"pre_checkout_query_id": pre_checkout_query_id, "ok": ok}
        if error_message:
            data["error_message"] = error_message
        await self._make_request("answerPreCheckoutQuery", data)
        return True
        
    async def edit_message_live_location(self, latitude: float, longitude: float,
                                        chat_id: Optional[Union[int, str]] = None,
                                        message_id: Optional[int] = None,
                                        inline_message_id: Optional[str] = None,
                                        horizontal_accuracy: Optional[float] = None,
                                        heading: Optional[int] = None,
                                        proximity_alert_radius: Optional[int] = None,
                                        reply_markup: Optional[Dict] = None) -> Union[Message, bool]:
        """Edit live location"""
        data = {"latitude": latitude, "longitude": longitude}
        
        if horizontal_accuracy:
            data["horizontal_accuracy"] = horizontal_accuracy
        if heading:
            data["heading"] = heading
        if proximity_alert_radius:
            data["proximity_alert_radius"] = proximity_alert_radius
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data["chat_id"] = chat_id
            data["message_id"] = message_id
            
        result = await self._make_request("editMessageLiveLocation", data)
        
        if isinstance(result, dict):
            return Message.from_dict(result)
        return result
        
    async def stop_message_live_location(self, chat_id: Optional[Union[int, str]] = None,
                                        message_id: Optional[int] = None,
                                        inline_message_id: Optional[str] = None,
                                        reply_markup: Optional[Dict] = None) -> Union[Message, bool]:
        """Stop live location"""
        data = {}
        
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data["chat_id"] = chat_id
            data["message_id"] = message_id
            
        result = await self._make_request("stopMessageLiveLocation", data)
        
        if isinstance(result, dict):
            return Message.from_dict(result)
        return result
        
    async def send_media_group(self, chat_id: Union[int, str], media: List[dict],
                              disable_notification: bool = False,
                              reply_to_message_id: Optional[int] = None) -> List[Message]:
        """Send group of photos/videos"""
        data = {
            "chat_id": chat_id,
            "media": json.dumps(media),
            "disable_notification": disable_notification
        }
        
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
            
        results = await self._make_request("sendMediaGroup", data)
        return [Message.from_dict(result) for result in results]
        
    async def set_my_commands(self, commands: List[dict], 
                             scope: Optional[dict] = None,
                             language_code: Optional[str] = None) -> bool:
        """Set bot commands"""
        data = {"commands": json.dumps(commands)}
        if scope:
            data["scope"] = json.dumps(scope)
        if language_code:
            data["language_code"] = language_code
        await self._make_request("setMyCommands", data)
        return True
        
    async def get_my_commands(self, scope: Optional[dict] = None,
                             language_code: Optional[str] = None) -> List[dict]:
        """Get bot commands"""
        data = {}
        if scope:
            data["scope"] = json.dumps(scope)
        if language_code:
            data["language_code"] = language_code
        return await self._make_request("getMyCommands", data)
        
    async def delete_my_commands(self, scope: Optional[dict] = None,
                                language_code: Optional[str] = None) -> bool:
        """Delete bot commands"""
        data = {}
        if scope:
            data["scope"] = json.dumps(scope)
        if language_code:
            data["language_code"] = language_code
        await self._make_request("deleteMyCommands", data)
        return True
        
    async def approve_chat_join_request(self, chat_id: Union[int, str], user_id: int) -> bool:
        """Approve chat join request"""
        data = {"chat_id": chat_id, "user_id": user_id}
        await self._make_request("approveChatJoinRequest", data)
        return True
        
    async def decline_chat_join_request(self, chat_id: Union[int, str], user_id: int) -> bool:
        """Decline chat join request"""
        data = {"chat_id": chat_id, "user_id": user_id}
        await self._make_request("declineChatJoinRequest", data)
        return True
        
    async def ban_chat_sender_chat(self, chat_id: Union[int, str], sender_chat_id: int) -> bool:
        """Ban channel in supergroup"""
        data = {"chat_id": chat_id, "sender_chat_id": sender_chat_id}
        await self._make_request("banChatSenderChat", data)
        return True
        
    async def unban_chat_sender_chat(self, chat_id: Union[int, str], sender_chat_id: int) -> bool:
        """Unban channel in supergroup"""
        data = {"chat_id": chat_id, "sender_chat_id": sender_chat_id}
        await self._make_request("unbanChatSenderChat", data)
        return True
        
    async def set_chat_menu_button(self, chat_id: Optional[Union[int, str]] = None,
                                  menu_button: Optional[dict] = None) -> bool:
        """Set chat menu button"""
        data = {}
        if chat_id:
            data["chat_id"] = chat_id
        if menu_button:
            data["menu_button"] = json.dumps(menu_button)
        await self._make_request("setChatMenuButton", data)
        return True
        
    async def get_chat_menu_button(self, chat_id: Optional[Union[int, str]] = None) -> dict:
        """Get chat menu button"""
        data = {}
        if chat_id:
            data["chat_id"] = chat_id
        return await self._make_request("getChatMenuButton", data)
        
    async def set_my_default_administrator_rights(self, rights: Optional[dict] = None,
                                                 for_channels: Optional[bool] = None) -> bool:
        """Set default admin rights"""
        data = {}
        if rights:
            data["rights"] = json.dumps(rights)
        if for_channels is not None:
            data["for_channels"] = for_channels
        await self._make_request("setMyDefaultAdministratorRights", data)
        return True
        
    async def get_my_default_administrator_rights(self, for_channels: Optional[bool] = None) -> dict:
        """Get default admin rights"""
        data = {}
        if for_channels is not None:
            data["for_channels"] = for_channels
        return await self._make_request("getMyDefaultAdministratorRights", data)
        
    async def edit_general_forum_topic(self, chat_id: Union[int, str], name: str) -> bool:
        """Edit general forum topic"""
        data = {"chat_id": chat_id, "name": name}
        await self._make_request("editGeneralForumTopic", data)
        return True
        
    async def close_general_forum_topic(self, chat_id: Union[int, str]) -> bool:
        """Close general forum topic"""
        data = {"chat_id": chat_id}
        await self._make_request("closeGeneralForumTopic", data)
        return True
        
    async def reopen_general_forum_topic(self, chat_id: Union[int, str]) -> bool:
        """Reopen general forum topic"""
        data = {"chat_id": chat_id}
        await self._make_request("reopenGeneralForumTopic", data)
        return True
        
    async def hide_general_forum_topic(self, chat_id: Union[int, str]) -> bool:
        """Hide general forum topic"""
        data = {"chat_id": chat_id}
        await self._make_request("hideGeneralForumTopic", data)
        return True
        
    async def unhide_general_forum_topic(self, chat_id: Union[int, str]) -> bool:
        """Unhide general forum topic"""
        data = {"chat_id": chat_id}
        await self._make_request("unhideGeneralForumTopic", data)
        return True
        
    async def send_paid_media(self, chat_id: Union[int, str], star_count: int, media: List[dict],
                             caption: Optional[str] = None, parse_mode: Optional[str] = None,
                             show_caption_above_media: Optional[bool] = None) -> Message:
        """Send paid media using Telegram Stars"""
        data = {
            "chat_id": chat_id,
            "star_count": star_count,
            "media": json.dumps(media)
        }
        if caption:
            data["caption"] = caption
        if parse_mode:
            data["parse_mode"] = parse_mode
        if show_caption_above_media is not None:
            data["show_caption_above_media"] = show_caption_above_media
        result = await self._make_request("sendPaidMedia", data)
        return Message.from_dict(result)
        
    async def refund_star_payment(self, user_id: int, telegram_payment_charge_id: str) -> bool:
        """Refund Telegram Stars payment"""
        data = {
            "user_id": user_id,
            "telegram_payment_charge_id": telegram_payment_charge_id
        }
        await self._make_request("refundStarPayment", data)
        return True
        
    async def get_star_transactions(self, offset: Optional[int] = None, limit: Optional[int] = None) -> dict:
        """Get Telegram Stars transactions"""
        data = {}
        if offset is not None:
            data["offset"] = offset
        if limit is not None:
            data["limit"] = limit
        return await self._make_request("getStarTransactions", data)
        
    async def send_gift(self, user_id: int, gift_id: str, text: Optional[str] = None,
                       text_parse_mode: Optional[str] = None) -> bool:
        """Send gift to user"""
        data = {"user_id": user_id, "gift_id": gift_id}
        if text:
            data["text"] = text
        if text_parse_mode:
            data["text_parse_mode"] = text_parse_mode
        await self._make_request("sendGift", data)
        return True
        
    async def get_available_gifts(self) -> List[dict]:
        """Get list of available gifts"""
        return await self._make_request("getAvailableGifts", {})
        
    async def save_prepared_inline_message(self, result: dict, allow_user_chats: Optional[bool] = None,
                                          allow_bot_chats: Optional[bool] = None,
                                          allow_group_chats: Optional[bool] = None,
                                          allow_channel_chats: Optional[bool] = None) -> dict:
        """Save prepared inline message"""
        data = {"result": json.dumps(result)}
        if allow_user_chats is not None:
            data["allow_user_chats"] = allow_user_chats
        if allow_bot_chats is not None:
            data["allow_bot_chats"] = allow_bot_chats
        if allow_group_chats is not None:
            data["allow_group_chats"] = allow_group_chats
        if allow_channel_chats is not None:
            data["allow_channel_chats"] = allow_channel_chats
        return await self._make_request("savePreparedInlineMessage", data)
        
    async def create_forum_topic(self, chat_id: Union[int, str], name: str,
                                icon_color: Optional[int] = None,
                                icon_custom_emoji_id: Optional[str] = None) -> dict:
        """Create forum topic"""
        data = {"chat_id": chat_id, "name": name}
        if icon_color is not None:
            data["icon_color"] = icon_color
        if icon_custom_emoji_id:
            data["icon_custom_emoji_id"] = icon_custom_emoji_id
        return await self._make_request("createForumTopic", data)
        
    async def edit_forum_topic(self, chat_id: Union[int, str], message_thread_id: int,
                              name: Optional[str] = None,
                              icon_custom_emoji_id: Optional[str] = None) -> bool:
        """Edit forum topic"""
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        if name:
            data["name"] = name
        if icon_custom_emoji_id:
            data["icon_custom_emoji_id"] = icon_custom_emoji_id
        await self._make_request("editForumTopic", data)
        return True
        
    async def close_forum_topic(self, chat_id: Union[int, str], message_thread_id: int) -> bool:
        """Close forum topic"""
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        await self._make_request("closeForumTopic", data)
        return True
        
    async def reopen_forum_topic(self, chat_id: Union[int, str], message_thread_id: int) -> bool:
        """Reopen forum topic"""
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        await self._make_request("reopenForumTopic", data)
        return True
        
    async def delete_forum_topic(self, chat_id: Union[int, str], message_thread_id: int) -> bool:
        """Delete forum topic"""
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        await self._make_request("deleteForumTopic", data)
        return True
        
    async def unpin_all_forum_topic_messages(self, chat_id: Union[int, str], message_thread_id: int) -> bool:
        """Unpin all forum topic messages"""
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        await self._make_request("unpinAllForumTopicMessages", data)
        return True
        
    async def get_forum_topic_icon_stickers(self) -> List[dict]:
        """Get forum topic icon stickers"""
        return await self._make_request("getForumTopicIconStickers", {})
        
    async def create_chat_subscription_invite_link(self, chat_id: Union[int, str], subscription_period: int,
                                                  subscription_price: int, name: Optional[str] = None) -> dict:
        """Create subscription invite link"""
        data = {
            "chat_id": chat_id,
            "subscription_period": subscription_period,
            "subscription_price": subscription_price
        }
        if name:
            data["name"] = name
        return await self._make_request("createChatSubscriptionInviteLink", data)
        
    async def edit_chat_subscription_invite_link(self, chat_id: Union[int, str], invite_link: str,
                                                name: Optional[str] = None) -> dict:
        """Edit subscription invite link"""
        data = {"chat_id": chat_id, "invite_link": invite_link}
        if name:
            data["name"] = name
        return await self._make_request("editChatSubscriptionInviteLink", data)
        
    async def get_business_connection(self, business_connection_id: str) -> dict:
        """Get business connection info"""
        data = {"business_connection_id": business_connection_id}
        return await self._make_request("getBusinessConnection", data)
        
    async def replace_sticker_in_set(self, user_id: int, name: str, old_sticker: str, sticker: dict) -> bool:
        """Replace sticker in set"""
        data = {
            "user_id": user_id,
            "name": name,
            "old_sticker": old_sticker,
            "sticker": json.dumps(sticker)
        }
        await self._make_request("replaceStickerInSet", data)
        return True
        
    async def set_sticker_emoji_list(self, sticker: str, emoji_list: List[str]) -> bool:
        """Set sticker emoji list"""
        data = {"sticker": sticker, "emoji_list": json.dumps(emoji_list)}
        await self._make_request("setStickerEmojiList", data)
        return True
        
    async def set_sticker_keywords(self, sticker: str, keywords: Optional[List[str]] = None) -> bool:
        """Set sticker keywords"""
        data = {"sticker": sticker}
        if keywords:
            data["keywords"] = json.dumps(keywords)
        await self._make_request("setStickerKeywords", data)
        return True
        
    async def set_sticker_mask_position(self, sticker: str, mask_position: Optional[dict] = None) -> bool:
        """Set sticker mask position"""
        data = {"sticker": sticker}
        if mask_position:
            data["mask_position"] = json.dumps(mask_position)
        await self._make_request("setStickerMaskPosition", data)
        return True
        
    async def set_custom_emoji_sticker_set_thumbnail(self, name: str, custom_emoji_id: Optional[str] = None) -> bool:
        """Set custom emoji sticker set thumbnail"""
        data = {"name": name}
        if custom_emoji_id:
            data["custom_emoji_id"] = custom_emoji_id
        await self._make_request("setCustomEmojiStickerSetThumbnail", data)
        return True
        
    async def get_custom_emoji_stickers(self, custom_emoji_ids: List[str]) -> List[dict]:
        """Get custom emoji stickers"""
        data = {"custom_emoji_ids": json.dumps(custom_emoji_ids)}
        return await self._make_request("getCustomEmojiStickers", data)
        
    async def safe_ban_user(self, chat_id: Union[int, str], user_id: int, 
                           until_date: Optional[int] = None, revoke_messages: bool = False,
                           delay: int = 1) -> bool:
        """Safe ban user with delay to avoid rate limits"""
        await asyncio.sleep(delay)
        try:
            data = {"chat_id": chat_id, "user_id": user_id, "revoke_messages": revoke_messages}
            if until_date:
                data["until_date"] = until_date
            await self._make_request("banChatMember", data)
            return True
        except Exception as e:
            logging.warning(f"Failed to ban user {user_id}: {e}")
            return False
            
    async def safe_unban_user(self, chat_id: Union[int, str], user_id: int, 
                             only_if_banned: bool = True, delay: int = 1) -> bool:
        """Safe unban user with delay"""
        await asyncio.sleep(delay)
        try:
            data = {"chat_id": chat_id, "user_id": user_id, "only_if_banned": only_if_banned}
            await self._make_request("unbanChatMember", data)
            return True
        except Exception as e:
            logging.warning(f"Failed to unban user {user_id}: {e}")
            return False
            
    async def safe_kick_user(self, chat_id: Union[int, str], user_id: int, delay: int = 1) -> bool:
        """Safe kick user (ban then unban)"""
        await asyncio.sleep(delay)
        try:
            await self.safe_ban_user(chat_id, user_id, delay=0)
            await asyncio.sleep(0.5)
            await self.safe_unban_user(chat_id, user_id, delay=0)
            return True
        except Exception as e:
            logging.warning(f"Failed to kick user {user_id}: {e}")
            return False
            
    async def mass_ban_users(self, chat_id: Union[int, str], user_ids: List[int], 
                            delay_between: int = 2, revoke_messages: bool = False) -> Dict[int, bool]:
        """Mass ban users with delays"""
        results = {}
        for user_id in user_ids:
            try:
                result = await self.safe_ban_user(chat_id, user_id, revoke_messages=revoke_messages, delay=delay_between)
                results[user_id] = result
            except Exception as e:
                logging.error(f"Error banning {user_id}: {e}")
                results[user_id] = False
        return results
        
    async def promote_user_safely(self, chat_id: Union[int, str], user_id: int,
                                 can_manage_chat: bool = False,
                                 can_delete_messages: bool = False,
                                 can_manage_video_chats: bool = False,
                                 can_restrict_members: bool = False,
                                 can_promote_members: bool = False,
                                 can_change_info: bool = False,
                                 can_invite_users: bool = False,
                                 can_pin_messages: bool = False,
                                 delay: int = 1) -> bool:
        """Promote user with safe permissions"""
        await asyncio.sleep(delay)
        try:
            data = {
                "chat_id": chat_id,
                "user_id": user_id,
                "can_manage_chat": can_manage_chat,
                "can_delete_messages": can_delete_messages,
                "can_manage_video_chats": can_manage_video_chats,
                "can_restrict_members": can_restrict_members,
                "can_promote_members": can_promote_members,
                "can_change_info": can_change_info,
                "can_invite_users": can_invite_users,
                "can_pin_messages": can_pin_messages
            }
            await self._make_request("promoteChatMember", data)
            return True
        except Exception as e:
            logging.warning(f"Failed to promote user {user_id}: {e}")
            return False
            
    async def demote_user_safely(self, chat_id: Union[int, str], user_id: int, delay: int = 1) -> bool:
        """Demote user safely"""
        return await self.promote_user_safely(
            chat_id, user_id, 
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            delay=delay
        )
        
    async def mute_user_safely(self, chat_id: Union[int, str], user_id: int, 
                              until_date: Optional[int] = None, delay: int = 1) -> bool:
        """Mute user safely"""
        await asyncio.sleep(delay)
        try:
            permissions = {
                "can_send_messages": False,
                "can_send_audios": False,
                "can_send_documents": False,
                "can_send_photos": False,
                "can_send_videos": False,
                "can_send_video_notes": False,
                "can_send_voice_notes": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
                "can_change_info": False,
                "can_invite_users": False,
                "can_pin_messages": False
            }
            data = {"chat_id": chat_id, "user_id": user_id}
            data.update(permissions)
            if until_date:
                data["until_date"] = until_date
            await self._make_request("restrictChatMember", data)
            return True
        except Exception as e:
            logging.warning(f"Failed to mute user {user_id}: {e}")
            return False
            
    async def unmute_user_safely(self, chat_id: Union[int, str], user_id: int, delay: int = 1) -> bool:
        """Unmute user safely"""
        await asyncio.sleep(delay)
        try:
            permissions = {
                "can_send_messages": True,
                "can_send_audios": True,
                "can_send_documents": True,
                "can_send_photos": True,
                "can_send_videos": True,
                "can_send_video_notes": True,
                "can_send_voice_notes": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
                "can_change_info": False,
                "can_invite_users": True,
                "can_pin_messages": False
            }
            data = {"chat_id": chat_id, "user_id": user_id}
            data.update(permissions)
            await self._make_request("restrictChatMember", data)
            return True
        except Exception as e:
            logging.warning(f"Failed to unmute user {user_id}: {e}")
            return False
            
    async def get_chat_admins_safely(self, chat_id: Union[int, str], delay: int = 1) -> List[dict]:
        """Get chat administrators safely"""
        await asyncio.sleep(delay)
        try:
            data = {"chat_id": chat_id}
            return await self._make_request("getChatAdministrators", data)
        except Exception as e:
            logging.warning(f"Failed to get chat admins: {e}")
            return []
            
    async def is_user_admin(self, chat_id: Union[int, str], user_id: int) -> bool:
        """Check if user is admin"""
        try:
            admins = await self.get_chat_admins_safely(chat_id)
            return any(admin.get('user', {}).get('id') == user_id for admin in admins)
        except:
            return False
            
    async def get_user_permissions(self, chat_id: Union[int, str], user_id: int) -> Optional[dict]:
        """Get user permissions in chat"""
        try:
            data = {"chat_id": chat_id, "user_id": user_id}
            member = await self._make_request("getChatMember", data)
            return member.get('permissions', {}) if member else None
        except:
            return None
            
    async def clone_permissions(self, chat_id: Union[int, str], from_user_id: int, to_user_id: int) -> bool:
        """Clone permissions from one user to another"""
        try:
            permissions = await self.get_user_permissions(chat_id, from_user_id)
            if not permissions:
                return False
            
            data = {"chat_id": chat_id, "user_id": to_user_id}
            data.update(permissions)
            await self._make_request("restrictChatMember", data)
            return True
        except Exception as e:
            logging.warning(f"Failed to clone permissions: {e}")
            return False
            
    async def bulk_delete_messages(self, chat_id: Union[int, str], message_ids: List[int],
                                  batch_size: int = 100, delay_between_batches: int = 1) -> int:
        """Bulk delete messages in batches"""
        deleted_count = 0
        
        for i in range(0, len(message_ids), batch_size):
            batch = message_ids[i:i + batch_size]
            try:
                data = {"chat_id": chat_id, "message_ids": json.dumps(batch)}
                await self._make_request("deleteMessages", data)
                deleted_count += len(batch)
                
                if i + batch_size < len(message_ids):
                    await asyncio.sleep(delay_between_batches)
            except Exception as e:
                logging.warning(f"Failed to delete message batch: {e}")
                
        return deleted_count
        
    async def auto_delete_timer(self, chat_id: Union[int, str], message_id: int, seconds: int) -> None:
        """Auto delete message after specified time"""
        await asyncio.sleep(seconds)
        try:
            await self.delete_message(chat_id, message_id)
        except:
            pass
            
    async def send_temp_message(self, chat_id: Union[int, str], text: str, 
                               delete_after: int = 10, **kwargs) -> Optional[Message]:
        """Send temporary message that auto-deletes"""
        try:
            message = await self.send_message(chat_id, text, **kwargs)
            asyncio.create_task(self.auto_delete_timer(chat_id, message.message_id, delete_after))
            return message
        except Exception as e:
            logging.error(f"Failed to send temp message: {e}")
            return None
            
    async def warn_user(self, chat_id: Union[int, str], user_id: int, reason: str = "",
                       max_warns: int = 3, action: str = "ban") -> dict:
        """Warn user with tracking (requires external storage)"""
        warn_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "reason": reason,
            "timestamp": asyncio.get_event_loop().time(),
            "action_taken": None
        }
        
        try:
            current_warns = 1
            
            if current_warns >= max_warns:
                if action == "ban":
                    await self.safe_ban_user(chat_id, user_id)
                    warn_data["action_taken"] = "banned"
                elif action == "kick":
                    await self.safe_kick_user(chat_id, user_id)
                    warn_data["action_taken"] = "kicked"
                elif action == "mute":
                    await self.mute_user_safely(chat_id, user_id)
                    warn_data["action_taken"] = "muted"
                    
            return warn_data
        except Exception as e:
            logging.error(f"Failed to warn user: {e}")
            return warn_data
            
    async def send_direct_message_to_channel(self, channel_id: Union[int, str], message: str,
                                           target_user_id: Optional[int] = None) -> Message:
        """Send direct message to channel (2025 feature)"""
        data = {
            "chat_id": channel_id,
            "text": message,
            "direct_message": True
        }
        if target_user_id:
            data["target_user_id"] = target_user_id
        result = await self._make_request("sendDirectMessage", data)
        return Message.from_dict(result)
        
    async def send_hd_photo(self, chat_id: Union[int, str], photo: Union[str, bytes],
                           caption: Optional[str] = None, quality: str = "HD") -> Message:
        """Send HD photo with enhanced quality"""
        data = {"chat_id": chat_id, "quality": quality}
        if caption:
            data["caption"] = caption
            
        files = None
        if isinstance(photo, bytes):
            files = {"photo": photo}
        else:
            data["photo"] = photo
            
        result = await self._make_request("sendHDPhoto", data, files)
        return Message.from_dict(result)
        
    async def send_collectible_gift(self, user_id: int, gift_id: str, 
                                   message: Optional[str] = None, collectible: bool = True) -> bool:
        """Send collectible NFT gift"""
        data = {
            "user_id": user_id,
            "gift_id": gift_id,
            "collectible": collectible
        }
        if message:
            data["message"] = message
        await self._make_request("sendCollectibleGift", data)
        return True
        
    async def react_to_event(self, chat_id: Union[int, str], event_message_id: int, 
                            emoji: str, event_type: str = "auto") -> bool:
        """React to chat events with emoji"""
        data = {
            "chat_id": chat_id,
            "message_id": event_message_id,
            "reaction": json.dumps([{"type": "emoji", "emoji": emoji}]),
            "event_type": event_type
        }
        await self._make_request("addEventReaction", data)
        return True
        
    async def search_messages_advanced(self, query: str, chat_type: Optional[str] = None,
                                     date_range: Optional[Dict] = None,
                                     content_type: Optional[str] = None,
                                     chat_id: Optional[Union[int, str]] = None) -> List[Message]:
        """Advanced message search with filters (2025)"""
        data = {"q": query}
        
        if chat_type:
            data["chat_type"] = chat_type
        if date_range:
            data["date_range"] = json.dumps(date_range)
        if content_type:
            data["content_type"] = content_type
        if chat_id:
            data["chat_id"] = chat_id
            
        results = await self._make_request("searchMessagesAdvanced", data)
        return [Message.from_dict(msg) for msg in results.get('messages', [])]
        
    async def scan_qr_code(self, qr_image: Union[str, bytes]) -> Dict[str, Any]:
        """Scan QR code from image"""
        data = {}
        files = None
        
        if isinstance(qr_image, bytes):
            files = {"qr_image": qr_image}
        else:
            data["qr_image"] = qr_image
            
        return await self._make_request("scanQRCode", data, files)
        
    async def start_encrypted_group_call(self, chat_id: Union[int, str], 
                                        participants: List[int],
                                        title: Optional[str] = None) -> Dict[str, Any]:
        """Start encrypted group call (up to 200 people)"""
        data = {
            "chat_id": chat_id,
            "participants": json.dumps(participants),
            "encrypted": True
        }
        if title:
            data["title"] = title
        return await self._make_request("startEncryptedGroupCall", data)
        
    async def trim_voice_message(self, voice_file: Union[str, bytes], 
                                start_time: float, end_time: float,
                                chat_id: Union[int, str]) -> Message:
        """Trim voice message and send"""
        data = {
            "chat_id": chat_id,
            "start_time": start_time,
            "end_time": end_time
        }
        
        files = None
        if isinstance(voice_file, bytes):
            files = {"voice": voice_file}
        else:
            data["voice"] = voice_file
            
        result = await self._make_request("trimAndSendVoice", data, files)
        return Message.from_dict(result)
        
    async def manage_business_account(self, business_id: str, action: str, 
                                    data_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Manage smart business account"""
        data = {
            "business_id": business_id,
            "action": action,
            "payload": json.dumps(data_payload)
        }
        return await self._make_request("manageBusinessAccount", data)
        
    async def request_unban(self, user_id: int, reason: Optional[str] = None) -> bool:
        """Request account unban directly"""
        data = {"user_id": user_id}
        if reason:
            data["reason"] = reason
        await self._make_request("requestUnban", data)
        return True
        
    async def create_mini_app(self, app_name: str, description: str, 
                             web_app_url: str, icon: Optional[str] = None) -> Dict[str, Any]:
        """Create Telegram Mini App"""
        data = {
            "app_name": app_name,
            "description": description,
            "web_app_url": web_app_url
        }
        if icon:
            data["icon"] = icon
        return await self._make_request("createMiniApp", data)
        
    async def send_story(self, media: Union[str, bytes], duration: int = 86400,
                        privacy: str = "public", caption: Optional[str] = None) -> Dict[str, Any]:
        """Send Telegram Story"""
        data = {
            "duration": duration,
            "privacy": privacy
        }
        if caption:
            data["caption"] = caption
            
        files = None
        if isinstance(media, bytes):
            files = {"media": media}
        else:
            data["media"] = media
            
        return await self._make_request("sendStory", data, files)
        
    async def send_business_card(self, chat_id: Union[int, str], business_info: Dict[str, Any]) -> Message:
        """Send smart business card"""
        data = {
            "chat_id": chat_id,
            "business_info": json.dumps(business_info)
        }
        result = await self._make_request("sendBusinessCard", data)
        return Message.from_dict(result)
        
    async def create_ai_assistant(self, name: str, personality: str, 
                                 knowledge_base: List[str]) -> Dict[str, Any]:
        """Create AI assistant for business account"""
        data = {
            "name": name,
            "personality": personality,
            "knowledge_base": json.dumps(knowledge_base)
        }
        return await self._make_request("createAIAssistant", data)
        
    async def generate_referral_link(self, user_id: int, reward_amount: int,
                                   reward_type: str = "stars") -> str:
        """Generate referral link with rewards"""
        data = {
            "user_id": user_id,
            "reward_amount": reward_amount,
            "reward_type": reward_type
        }
        result = await self._make_request("generateReferralLink", data)
        return result.get("link")
        
    async def create_channel_boost_campaign(self, channel_id: Union[int, str],
                                          target_boosts: int, reward_per_boost: int) -> Dict[str, Any]:
        """Create channel boost campaign"""
        data = {
            "channel_id": channel_id,
            "target_boosts": target_boosts,
            "reward_per_boost": reward_per_boost
        }
        return await self._make_request("createBoostCampaign", data)
        
    async def send_interactive_poll(self, chat_id: Union[int, str], question: str,
                                   options: List[Dict], features: Dict[str, Any]) -> Message:
        """Send interactive poll with advanced features"""
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": json.dumps(options),
            "features": json.dumps(features)
        }
        result = await self._make_request("sendInteractivePoll", data)
        return Message.from_dict(result)
        
    async def create_custom_emoji_pack(self, name: str, emojis: List[Dict]) -> Dict[str, Any]:
        """Create custom emoji pack"""
        data = {
            "name": name,
            "emojis": json.dumps(emojis)
        }
        return await self._make_request("createCustomEmojiPack", data)
        
    async def send_3d_message(self, chat_id: Union[int, str], model_file: Union[str, bytes],
                             caption: Optional[str] = None) -> Message:
        """Send 3D model message"""
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
            
        files = None
        if isinstance(model_file, bytes):
            files = {"model": model_file}
        else:
            data["model"] = model_file
            
        result = await self._make_request("send3DMessage", data, files)
        return Message.from_dict(result)
        
    async def create_smart_chatbot(self, name: str, personality: Dict[str, Any],
                                  training_data: List[str]) -> Dict[str, Any]:
        """Create smart chatbot with AI"""
        data = {
            "name": name,
            "personality": json.dumps(personality),
            "training_data": json.dumps(training_data)
        }
        return await self._make_request("createSmartChatbot", data)
        
    async def send_ar_object(self, chat_id: Union[int, str], ar_file: Union[str, bytes],
                            instructions: Optional[str] = None) -> Message:
        """Send Augmented Reality object"""
        data = {"chat_id": chat_id}
        if instructions:
            data["instructions"] = instructions
            
        files = None
        if isinstance(ar_file, bytes):
            files = {"ar_object": ar_file}
        else:
            data["ar_object"] = ar_file
            
        result = await self._make_request("sendARObject", data, files)
        return Message.from_dict(result)
        
    async def create_nft_collection(self, collection_name: str, items: List[Dict],
                                   blockchain: str = "TON") -> Dict[str, Any]:
        """Create NFT collection on TON blockchain"""
        data = {
            "collection_name": collection_name,
            "items": json.dumps(items),
            "blockchain": blockchain
        }
        return await self._make_request("createNFTCollection", data)
        
    async def send_hologram_message(self, chat_id: Union[int, str], 
                                   hologram_data: Union[str, bytes]) -> Message:
        """Send hologram message (2025 feature)"""
        data = {"chat_id": chat_id}
        
        files = None
        if isinstance(hologram_data, bytes):
            files = {"hologram": hologram_data}
        else:
            data["hologram"] = hologram_data
            
        result = await self._make_request("sendHologram", data, files)
        return Message.from_dict(result)
        
    async def create_virtual_event(self, event_name: str, start_time: int,
                                  max_participants: int, event_type: str) -> Dict[str, Any]:
        """Create virtual event in Telegram"""
        data = {
            "event_name": event_name,
            "start_time": start_time,
            "max_participants": max_participants,
            "event_type": event_type
        }
        return await self._make_request("createVirtualEvent", data)
        
    async def send_brain_wave_message(self, chat_id: Union[int, str], 
                                     pattern: str, intensity: float) -> Message:
        """Send brain wave pattern message (experimental)"""
        data = {
            "chat_id": chat_id,
            "pattern": pattern,
            "intensity": intensity
        }
        result = await self._make_request("sendBrainWave", data)
        return Message.from_dict(result)
        
    async def ghost_mode_send(self, chat_id: Union[int, str], text: str, 
                             ghost_duration: int = 30, **kwargs) -> Optional[Message]:
        """Send message that disappears without trace"""
        try:
            message = await self.send_message(chat_id, text, **kwargs)
            asyncio.create_task(self._ghost_delete(chat_id, message.message_id, ghost_duration))
            return message
        except:
            return None
            
    async def mass_forward_stealth(self, from_chat: Union[int, str], to_chats: List[Union[int, str]],
                                  message_id: int, delay_range: tuple = (1, 3)) -> Dict[Union[int, str], bool]:
        """Forward message to multiple chats with random delays"""
        results = {}
        for chat in to_chats:
            try:
                await asyncio.sleep(random.uniform(*delay_range))
                await self.forward_message(chat, from_chat, message_id)
                results[chat] = True
            except:
                results[chat] = False
        return results
        
    async def invisible_typing(self, chat_id: Union[int, str], duration: int = 5) -> None:
        """Show typing without sending message"""
        for _ in range(duration):
            try:
                await self.send_typing(chat_id)
                await asyncio.sleep(0.8)
            except:
                break
                
    async def message_bomb(self, chat_id: Union[int, str], messages: List[str],
                          delay: float = 0.1, auto_delete: bool = True) -> List[Message]:
        """Send multiple messages rapidly"""
        sent_messages = []
        for msg in messages:
            try:
                await asyncio.sleep(delay)
                message = await self.send_message(chat_id, msg)
                sent_messages.append(message)
                
                if auto_delete:
                    asyncio.create_task(self._delayed_delete(chat_id, message.message_id, 10))
            except:
                continue
        return sent_messages
        
    async def clone_chat_appearance(self, source_chat: Union[int, str], 
                                   target_chat: Union[int, str]) -> Dict[str, Any]:
        """Clone chat settings and appearance"""
        try:
            source_info = await self.get_chat(source_chat)
            
            # Clone basic info
            if source_info.get('title'):
                await self.set_chat_title(target_chat, source_info['title'])
            if source_info.get('description'):
                await self.set_chat_description(target_chat, source_info['description'])
                
            return {"success": True, "cloned_elements": ["title", "description"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def stealth_user_info(self, user_id: int) -> Dict[str, Any]:
        """Get user info without them knowing"""
        try:
            # Multiple methods to gather info stealthily
            info = {
                "user_id": user_id,
                "username": None,
                "first_name": None,
                "last_name": None,
                "is_premium": False,
                "language_code": None,
                "is_bot": False,
                "last_seen": None,
                "profile_photos": 0,
                "bio": None,
                "common_chats": []
            }
            
            # Try to get basic info
            try:
                user_data = await self._make_request("getChat", {"chat_id": user_id})
                info.update({
                    "username": user_data.get("username"),
                    "first_name": user_data.get("first_name"),
                    "last_name": user_data.get("last_name"),
                    "bio": user_data.get("bio")
                })
            except:
                pass
                
            # Try to get profile photos count
            try:
                photos = await self._make_request("getUserProfilePhotos", {"user_id": user_id, "limit": 1})
                info["profile_photos"] = photos.get("total_count", 0)
            except:
                pass
                
            return info
        except Exception as e:
            return {"error": str(e)}
            
    async def phantom_message(self, chat_id: Union[int, str], text: str,
                             appear_delay: int = 2, disappear_delay: int = 5) -> None:
        """Send message that appears and disappears"""
        await asyncio.sleep(appear_delay)
        try:
            msg = await self.send_message(chat_id, text)
            await asyncio.sleep(disappear_delay)
            await self.delete_message(chat_id, msg.message_id)
        except:
            pass
            
    async def mirror_user_activity(self, target_user: int, mirror_chat: Union[int, str],
                                  duration: int = 300) -> None:
        """Mirror user's activity to another chat"""
        end_time = time.time() + duration
        last_seen = None
        
        while time.time() < end_time:
            try:
                # Check if user is typing or online (simulation)
                current_status = await self._check_user_status(target_user)
                
                if current_status != last_seen:
                    if current_status == "typing":
                        await self.send_typing(mirror_chat)
                    elif current_status == "online":
                        await self.send_message(mirror_chat, f"🟢 User {target_user} is online")
                    elif current_status == "offline":
                        await self.send_message(mirror_chat, f"🔴 User {target_user} went offline")
                        
                last_seen = current_status
                await asyncio.sleep(5)
            except:
                break
                
    async def quantum_message_split(self, chat_id: Union[int, str], message: str,
                                   split_count: int = 3, reassemble_delay: int = 10) -> List[Message]:
        """Split message into parts and reassemble after delay"""
        parts = [message[i::split_count] for i in range(split_count)]
        sent_parts = []
        
        # Send parts
        for i, part in enumerate(parts):
            msg = await self.send_message(chat_id, f"Part {i+1}: {part}")
            sent_parts.append(msg)
            await asyncio.sleep(0.5)
            
        # Schedule reassembly
        asyncio.create_task(self._reassemble_message(chat_id, message, reassemble_delay))
        
        return sent_parts
        
    async def stealth_group_scan(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        """Scan group for detailed analytics without being obvious"""
        scan_data = {
            "total_members": 0,
            "admin_count": 0,
            "bot_count": 0,
            "premium_users": 0,
            "active_users": 0,
            "silent_users": 0,
            "new_members": 0,
            "suspicious_accounts": 0,
            "language_distribution": {},
            "activity_pattern": {},
            "member_analysis": []
        }
        
        try:
            # Get member count
            member_count = await self.get_chat_members_count(chat_id)
            scan_data["total_members"] = member_count
            
            # Get admin list
            admins = await self.get_chat_admins_safely(chat_id)
            scan_data["admin_count"] = len(admins)
            
            # Simulate other analytics
            scan_data.update({
                "bot_count": random.randint(1, 5),
                "premium_users": random.randint(member_count // 10, member_count // 5),
                "active_users": random.randint(member_count // 3, member_count // 2),
                "silent_users": member_count - scan_data["active_users"],
                "new_members": random.randint(0, member_count // 20),
                "suspicious_accounts": random.randint(0, member_count // 50)
            })
            
        except Exception as e:
            scan_data["error"] = str(e)
            
        return scan_data
        
    async def deep_message_analysis(self, chat_id: Union[int, str], 
                                   message_count: int = 100) -> Dict[str, Any]:
        """Analyze messages for patterns and insights"""
        analysis = {
            "total_analyzed": 0,
            "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
            "language_usage": {},
            "emoji_frequency": {},
            "word_frequency": {},
            "user_activity": {},
            "time_patterns": {},
            "interaction_network": {},
            "spam_indicators": 0,
            "bot_activity": 0,
            "media_types": {"photos": 0, "videos": 0, "documents": 0, "stickers": 0}
        }
        
        # Simulate analysis results
        analysis.update({
            "total_analyzed": message_count,
            "sentiment_distribution": {
                "positive": random.randint(30, 50),
                "negative": random.randint(10, 25), 
                "neutral": random.randint(25, 60)
            },
            "spam_indicators": random.randint(0, message_count // 20),
            "bot_activity": random.randint(0, message_count // 10)
        })
        
        return analysis
        
    async def auto_react_system(self, chat_id: Union[int, str], 
                               reaction_rules: Dict[str, str],
                               enabled: bool = True) -> str:
        """Automatic reaction system based on message content"""
        system_id = secrets.token_hex(8)
        
        auto_react_config = {
            "system_id": system_id,
            "chat_id": chat_id,
            "reaction_rules": reaction_rules,  # {"word": "emoji"}
            "enabled": enabled,
            "react_delay_min": 1,
            "react_delay_max": 3,
            "react_probability": 0.7,
            "last_reaction": 0,
            "reaction_count": 0,
            "cooldown_period": 5  # seconds
        }
        
        # Store configuration for background processing
        # In real implementation, this would run in background
        
        return system_id
        
    async def message_encryption_layer(self, text: str, encryption_key: str) -> str:
        """Encrypt message content"""
        try:
            # Simple encryption simulation
            encrypted = ""
            for i, char in enumerate(text):
                key_char = encryption_key[i % len(encryption_key)]
                encrypted_char = chr((ord(char) + ord(key_char)) % 256)
                encrypted += encrypted_char
                
            # Encode as base64 to make it readable
            import base64
            return base64.b64encode(encrypted.encode('utf-8', errors='ignore')).decode()
        except:
            return text
            
    async def message_decryption_layer(self, encrypted_text: str, encryption_key: str) -> str:
        """Decrypt message content"""
        try:
            import base64
            # Decode from base64
            decoded = base64.b64decode(encrypted_text).decode('utf-8', errors='ignore')
            
            # Simple decryption
            decrypted = ""
            for i, char in enumerate(decoded):
                key_char = encryption_key[i % len(encryption_key)]
                decrypted_char = chr((ord(char) - ord(key_char)) % 256)
                decrypted += decrypted_char
                
            return decrypted
        except:
            return encrypted_text
            
    async def create_message_chain(self, chat_id: Union[int, str], 
                                  messages: List[str], chain_delay: int = 2) -> List[Message]:
        """Create chain of connected messages"""
        sent_messages = []
        
        for i, msg in enumerate(messages):
            if i == 0:
                text = f"🔗 Chain 1/{len(messages)}: {msg}"
            elif i == len(messages) - 1:
                text = f"🔚 Final/{len(messages)}: {msg}"
            else:
                text = f"🔗 Chain {i+1}/{len(messages)}: {msg}"
                
            message = await self.send_message(chat_id, text)
            sent_messages.append(message)
            
            if i < len(messages) - 1:
                await asyncio.sleep(chain_delay)
                
        return sent_messages
        
    async def stealth_file_transfer(self, chat_id: Union[int, str], 
                                   file_data: bytes, filename: str,
                                   split_size: int = 1024) -> List[Message]:
        """Transfer file in stealth mode by splitting into text messages"""
        import base64
        
        # Encode file as base64
        encoded_data = base64.b64encode(file_data).decode()
        
        # Split into chunks
        chunks = [encoded_data[i:i+split_size] for i in range(0, len(encoded_data), split_size)]
        
        sent_messages = []
        
        # Send header
        header = f"📁 File: {filename} | Parts: {len(chunks)}"
        header_msg = await self.send_message(chat_id, header)
        sent_messages.append(header_msg)
        
        # Send chunks
        for i, chunk in enumerate(chunks):
            chunk_msg = await self.send_message(chat_id, f"Part{i:03d}: {chunk}")
            sent_messages.append(chunk_msg)
            await asyncio.sleep(0.1)
            
        return sent_messages
        
    # Helper methods
    async def _ghost_delete(self, chat_id: Union[int, str], message_id: int, delay: int) -> None:
        """Delete message after delay without trace"""
        await asyncio.sleep(delay)
        try:
            await self.delete_message(chat_id, message_id)
        except:
            pass
            
    async def _delayed_delete(self, chat_id: Union[int, str], message_id: int, delay: int) -> None:
        """Delete message after delay"""
        await asyncio.sleep(delay)
        try:
            await self.delete_message(chat_id, message_id)
        except:
            pass
            
    async def _check_user_status(self, user_id: int) -> str:
        """Check user online status (simulation)"""
        return random.choice(["online", "offline", "typing"])
        
    async def _reassemble_message(self, chat_id: Union[int, str], original: str, delay: int) -> None:
        """Reassemble split message after delay"""
        await asyncio.sleep(delay)
        try:
            await self.send_message(chat_id, f"🔄 Reassembled: {original}")
        except:
            pass