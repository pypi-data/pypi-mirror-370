"""
فیچرهای پیشرفته و خفن PyMn
"""

import asyncio
import json
import sqlite3
import pickle
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from .utils import Cache, RateLimiter


class StateManager:
    """مدیریت state کاربران"""
    
    def __init__(self, db_path: str = "states.db"):
        """
        ساخت مدیر state
        
        Args:
            db_path: مسیر فایل دیتابیس
        """
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """ایجاد جدول‌های دیتابیس"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def set_state(self, user_id: int, state: str, data: Dict = None):
        """تنظیم state کاربر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_json = json.dumps(data or {})
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_states (user_id, state, data, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, state, data_json, datetime.now()))
        
        conn.commit()
        conn.close()
        
    def get_state(self, user_id: int) -> tuple:
        """دریافت state کاربر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT state, data FROM user_states WHERE user_id = ?',
            (user_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            state, data_json = result
            data = json.loads(data_json) if data_json else {}
            return state, data
            
        return None, {}
        
    def clear_state(self, user_id: int):
        """پاک کردن state کاربر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()


class ConversationHandler:
    """مدیریت مکالمات چندمرحله‌ای"""
    
    def __init__(self, bot, timeout: int = 300):
        """
        ساخت مدیر مکالمه
        
        Args:
            bot: instance ربات
            timeout: مدت انقضا مکالمه (ثانیه)
        """
        self.bot = bot
        self.timeout = timeout
        self.conversations: Dict[int, Dict] = {}
        self.state_manager = StateManager()
        
    def start_conversation(self, user_id: int, steps: List[Dict]):
        """
        شروع مکالمه جدید
        
        Args:
            user_id: شناسه کاربر
            steps: مراحل مکالمه
            
        مثال:
            steps = [
                {"message": "نام شما چیست؟", "key": "name"},
                {"message": "سن شما چقدر است؟", "key": "age", "type": "int"},
                {"message": "شهر شما کدام است؟", "key": "city"}
            ]
        """
        self.conversations[user_id] = {
            "steps": steps,
            "current_step": 0,
            "data": {},
            "started_at": datetime.now()
        }
        
        # تنظیم state
        self.state_manager.set_state(user_id, "conversation", {"step": 0})
        
    async def process_message(self, message) -> bool:
        """
        پردازش پیام در مکالمه
        
        Args:
            message: پیام کاربر
            
        Returns:
            True اگر پیام در مکالمه پردازش شد
        """
        user_id = message.from_user.id
        
        if user_id not in self.conversations:
            return False
            
        conversation = self.conversations[user_id]
        
        # بررسی انقضا
        if datetime.now() - conversation["started_at"] > timedelta(seconds=self.timeout):
            self.end_conversation(user_id)
            await self.bot.send_message(
                message.chat.id,
                "⏰ مکالمه منقضی شد. لطفاً دوباره شروع کنید."
            )
            return True
            
        current_step = conversation["current_step"]
        steps = conversation["steps"]
        
        if current_step >= len(steps):
            return False
            
        step = steps[current_step]
        
        # اعتبارسنجی ورودی
        value = message.text
        if step.get("type") == "int":
            try:
                value = int(value)
            except ValueError:
                await self.bot.send_message(
                    message.chat.id,
                    "❌ لطفاً یک عدد وارد کنید."
                )
                return True
                
        # ذخیره پاسخ
        conversation["data"][step["key"]] = value
        
        # مرحله بعدی
        conversation["current_step"] += 1
        
        if conversation["current_step"] >= len(steps):
            # پایان مکالمه
            await self.complete_conversation(user_id, message.chat.id)
        else:
            # ارسال سوال بعدی
            next_step = steps[conversation["current_step"]]
            await self.bot.send_message(
                message.chat.id,
                next_step["message"]
            )
            
        return True
        
    async def complete_conversation(self, user_id: int, chat_id: int):
        """تکمیل مکالمه"""
        if user_id in self.conversations:
            data = self.conversations[user_id]["data"]
            
            # ارسال خلاصه
            summary = "✅ اطلاعات شما:\n\n"
            for key, value in data.items():
                summary += f"• {key}: {value}\n"
                
            await self.bot.send_message(chat_id, summary)
            
            # پاک کردن مکالمه
            self.end_conversation(user_id)
            
    def end_conversation(self, user_id: int):
        """پایان مکالمه"""
        if user_id in self.conversations:
            del self.conversations[user_id]
        self.state_manager.clear_state(user_id)


class PluginManager:
    """مدیریت پلاگین‌ها"""
    
    def __init__(self, bot):
        """
        ساخت مدیر پلاگین
        
        Args:
            bot: instance ربات
        """
        self.bot = bot
        self.plugins: Dict[str, Any] = {}
        self.enabled_plugins: List[str] = []
        
    def register_plugin(self, name: str, plugin_class, config: Dict = None):
        """
        ثبت پلاگین جدید
        
        Args:
            name: نام پلاگین
            plugin_class: کلاس پلاگین
            config: تنظیمات پلاگین
        """
        self.plugins[name] = {
            "class": plugin_class,
            "config": config or {},
            "instance": None
        }
        
    def enable_plugin(self, name: str):
        """فعال کردن پلاگین"""
        if name in self.plugins and name not in self.enabled_plugins:
            plugin_info = self.plugins[name]
            plugin_info["instance"] = plugin_info["class"](self.bot, plugin_info["config"])
            self.enabled_plugins.append(name)
            
    def disable_plugin(self, name: str):
        """غیرفعال کردن پلاگین"""
        if name in self.enabled_plugins:
            self.enabled_plugins.remove(name)
            if name in self.plugins:
                self.plugins[name]["instance"] = None
                
    def get_plugin(self, name: str):
        """دریافت instance پلاگین"""
        if name in self.plugins and name in self.enabled_plugins:
            return self.plugins[name]["instance"]
        return None


class MessageQueue:
    """صف پیام‌ها برای ارسال تدریجی"""
    
    def __init__(self, bot, rate_limit: int = 30):
        """
        ساخت صف پیام
        
        Args:
            bot: instance ربات
            rate_limit: حداکثر پیام در دقیقه
        """
        self.bot = bot
        self.rate_limit = rate_limit
        self.queue: List[Dict] = []
        self.running = False
        
    def add_message(self, chat_id: int, text: str, **kwargs):
        """اضافه کردن پیام به صف"""
        self.queue.append({
            "chat_id": chat_id,
            "text": text,
            "kwargs": kwargs,
            "added_at": datetime.now()
        })
        
    async def start_processing(self):
        """شروع پردازش صف"""
        self.running = True
        delay = 60 / self.rate_limit  # تاخیر بین پیام‌ها
        
        while self.running:
            if self.queue:
                message_data = self.queue.pop(0)
                
                try:
                    await self.bot.send_message(
                        message_data["chat_id"],
                        message_data["text"],
                        **message_data["kwargs"]
                    )
                except Exception as e:
                    print(f"خطا در ارسال پیام: {e}")
                    
                await asyncio.sleep(delay)
            else:
                await asyncio.sleep(1)
                
    def stop_processing(self):
        """توقف پردازش صف"""
        self.running = False


class Analytics:
    """آمارگیری و تحلیل"""
    
    def __init__(self, db_path: str = "analytics.db"):
        """
        ساخت تحلیلگر
        
        Args:
            db_path: مسیر فایل دیتابیس
        """
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """ایجاد جدول‌های آمار"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                message_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_user_action(self, user_id: int, action: str, data: Dict = None):
        """ثبت فعالیت کاربر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activity (user_id, action, data)
            VALUES (?, ?, ?)
        ''', (user_id, action, json.dumps(data or {})))
        
        conn.commit()
        conn.close()
        
    def log_message(self, chat_id: int, user_id: int, message_type: str):
        """ثبت آمار پیام"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO message_stats (chat_id, user_id, message_type)
            VALUES (?, ?, ?)
        ''', (chat_id, user_id, message_type))
        
        conn.commit()
        conn.close()
        
    def get_user_stats(self, user_id: int) -> Dict:
        """دریافت آمار کاربر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # تعداد کل فعالیت‌ها
        cursor.execute(
            'SELECT COUNT(*) FROM user_activity WHERE user_id = ?',
            (user_id,)
        )
        total_actions = cursor.fetchone()[0]
        
        # تعداد پیام‌ها
        cursor.execute(
            'SELECT COUNT(*) FROM message_stats WHERE user_id = ?',
            (user_id,)
        )
        total_messages = cursor.fetchone()[0]
        
        # آخرین فعالیت
        cursor.execute(
            'SELECT timestamp FROM user_activity WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1',
            (user_id,)
        )
        last_activity = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_actions": total_actions,
            "total_messages": total_messages,
            "last_activity": last_activity[0] if last_activity else None
        }


class Scheduler:
    """زمان‌بند برای اجرای تسک‌های دوره‌ای"""
    
    def __init__(self):
        """ساخت زمان‌بند"""
        self.tasks: List[Dict] = []
        self.running = False
        
    def add_task(
        self,
        func: Callable,
        interval: int,
        args: tuple = (),
        kwargs: Dict = None,
        run_once: bool = False
    ):
        """
        اضافه کردن تسک
        
        Args:
            func: تابع برای اجرا
            interval: فاصله اجرا (ثانیه)
            args: آرگومان‌های تابع
            kwargs: keyword arguments
            run_once: اجرا فقط یکبار
        """
        self.tasks.append({
            "func": func,
            "interval": interval,
            "args": args or (),
            "kwargs": kwargs or {},
            "run_once": run_once,
            "last_run": None,
            "next_run": datetime.now() + timedelta(seconds=interval)
        })
        
    async def start(self):
        """شروع زمان‌بند"""
        self.running = True
        
        while self.running:
            now = datetime.now()
            
            for task in self.tasks[:]:  # کپی لیست برای تغییر ایمن
                if now >= task["next_run"]:
                    try:
                        if asyncio.iscoroutinefunction(task["func"]):
                            await task["func"](*task["args"], **task["kwargs"])
                        else:
                            task["func"](*task["args"], **task["kwargs"])
                            
                        task["last_run"] = now
                        
                        if task["run_once"]:
                            self.tasks.remove(task)
                        else:
                            task["next_run"] = now + timedelta(seconds=task["interval"])
                            
                    except Exception as e:
                        print(f"خطا در اجرای تسک: {e}")
                        
            await asyncio.sleep(1)
            
    def stop(self):
        """توقف زمان‌بند"""
        self.running = False


class BotAdmin:
    """پنل مدیریت ربات"""
    
    def __init__(self, bot, admin_ids: List[int]):
        """
        ساخت پنل ادمین
        
        Args:
            bot: instance ربات
            admin_ids: لیست شناسه ادمین‌ها
        """
        self.bot = bot
        self.admin_ids = admin_ids
        self.analytics = Analytics()
        
        # ثبت handler های ادمین
        self._register_admin_handlers()
        
    def _register_admin_handlers(self):
        """ثبت handler های مدیریتی"""
        
        @self.bot.command_handler("stats")
        async def stats_command(message):
            """نمایش آمار ربات"""
            if message.from_user.id not in self.admin_ids:
                return
                
            # محاسبه آمارها
            stats = await self._get_bot_stats()
            
            text = f"""
📊 آمار ربات:

👥 کل کاربران: {stats['total_users']}
💬 کل پیام‌ها: {stats['total_messages']}
📈 پیام‌های امروز: {stats['today_messages']}
⏰ آخرین فعالیت: {stats['last_activity']}
            """
            
            await self.bot.send_message(message.chat.id, text.strip())
            
        @self.bot.command_handler("broadcast")
        async def broadcast_command(message):
            """ارسال پیام همگانی"""
            if message.from_user.id not in self.admin_ids:
                return
                
            args = message.get_args()
            if not args:
                await self.bot.send_message(
                    message.chat.id,
                    "📢 استفاده: /broadcast متن پیام"
                )
                return
                
            broadcast_text = " ".join(args)
            
            # دریافت لیست کاربران
            users = await self._get_all_users()
            
            success_count = 0
            for user_id in users:
                try:
                    await self.bot.send_message(user_id, broadcast_text)
                    success_count += 1
                    await asyncio.sleep(0.1)  # تاخیر کم برای جلوگیری از rate limit
                except:
                    pass
                    
            await self.bot.send_message(
                message.chat.id,
                f"✅ پیام برای {success_count} کاربر ارسال شد."
            )
            
    async def _get_bot_stats(self) -> Dict:
        """محاسبه آمار ربات"""
        # این بخش باید با دیتابیس واقعی شما تطبیق داده شود
        return {
            "total_users": 0,
            "total_messages": 0,
            "today_messages": 0,
            "last_activity": "نامشخص"
        }
        
    async def _get_all_users(self) -> List[int]:
        """دریافت لیست تمام کاربران"""
        # این بخش باید با دیتابیس واقعی شما تطبیق داده شود
        return []
