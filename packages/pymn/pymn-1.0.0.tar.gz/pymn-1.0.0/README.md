# PyMn - کتابخانه قدرتمند ربات‌های تلگرام 🚀

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pymn.svg)](https://pypi.org/project/pymn/)

کتابخانه‌ای قدرتمند و کامل برای ساخت ربات‌های تلگرام با امکانات پیشرفته و استفاده آسان.

## ویژگی‌ها ✨

- 🔥 **ساده و قدرتمند**: API بسیار ساده با امکانات پیشرفته
- ⚡ **async/await**: پشتیبانی کامل از برنامه‌نویسی غیرهمزمان
- 🛡️ **امن**: مدیریت خطاها و validation داده‌ها
- 📱 **کامل**: پشتیبانی از تمام ویژگی‌های تلگرام
- 🎯 **بهینه**: عملکرد بالا و استفاده کم از منابع
- 🌐 **فارسی**: مستندات و پشتیبانی کامل فارسی

## نصب 📦

```bash
pip install pymn
```

## استفاده سریع 🚀

```python
import PyMn

# ساخت ربات
bot = PyMn.Bot("YOUR_BOT_TOKEN")

# پاسخ به پیام‌ها
@bot.message_handler()
async def handle_message(message):
    await bot.send_message(message.chat.id, f"سلام {message.from_user.first_name}!")

# اجرای ربات
bot.run()
```

## مثال‌های پیشرفته 💡

### کیبورد inline
```python
import PyMn

bot = PyMn.Bot("YOUR_TOKEN")

@bot.message_handler(commands=['start'])
async def start_command(message):
    keyboard = PyMn.InlineKeyboard()
    keyboard.add_button("🔥 دکمه خفن", callback_data="cool_button")
    keyboard.add_button("📊 آمار", callback_data="stats")
    
    await bot.send_message(
        message.chat.id, 
        "سلام! از کتابخانه PyMn استفاده می‌کنی 🚀",
        reply_markup=keyboard
    )

@bot.callback_query_handler()
async def handle_callback(callback):
    if callback.data == "cool_button":
        await bot.answer_callback_query(callback.id, "این دکمه واقعاً خفنه! 🔥")
```

### ارسال فایل و مدیا
```python
# ارسال عکس
await bot.send_photo(chat_id, "path/to/photo.jpg", caption="عکس خفن!")

# ارسال ویدیو
await bot.send_video(chat_id, "path/to/video.mp4")

# ارسال فایل
await bot.send_document(chat_id, "path/to/file.pdf")
```

### مدیریت گروه‌ها
```python
# اضافه کردن ادمین
await bot.promote_chat_member(chat_id, user_id)

# حذف کاربر
await bot.kick_chat_member(chat_id, user_id)

# تغییر تنظیمات گروه
await bot.set_chat_title(chat_id, "عنوان جدید گروه")
```

## مستندات 📚

برای مستندات کامل به [Wiki](https://github.com/DevMoEiN/PyMn/wiki) مراجعه کنید.

## مشارکت 🤝

مشارکت شما استقبال می‌شود! لطفاً [راهنمای مشارکت](CONTRIBUTING.md) را مطالعه کنید.

## لایسنس 📄

این پروژه تحت لایسنس MIT منتشر شده است. [LICENSE](LICENSE) را مشاهده کنید.

## حمایت 💖

اگر از PyMn استفاده می‌کنید و دوستش دارید، لطفاً یک ⭐ بدید!

---

ساخته شده با ❤️ توسط [DevMoEiN](https://github.com/DevMoEiN)
