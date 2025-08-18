# TeleNet


TeleNet یک کتابخانه مدرن و قدرتمند Python برای ساخت ربات‌های چت و مدیریت دستورهاست، با قابلیت Long Polling و طراحی ساده اما منعطف. با TeleNet می‌توانی ربات‌های پیچیده با پیام فارسی، دکمه کی‌برد، هندلینگ پیشرفته و مدیریت کامل کامندها بسازی، بدون دردسر و با کمترین کدنویسی.


---

## 🔹 ویژگی‌ها

- طراحی مدرن و سبک با asyncio

- پشتیبانی کامل از پیام‌های فارسی و Unicode

- سیستم Router & Command برای مدیریت کامندها

- امکان ساخت هندلرهای چندگانه برای دستورهای مختلف

- Long Polling ساده برای دریافت آپدیت‌ها

- کاملاً آماده برای گسترش و ماژولار شدن

- مناسب برای ربات‌های شخصی و عمومی



---

## 🔹 نصب
```bash

pip install telenet```

- > TeleNet نیاز به Python 3.10+ دارد.




---

🔹 شروع سریع
```python
import asyncio
from telenet import TeleNetClient, Router, Command

TOKEN = "<YOUR_BOT_TOKEN>"
bot = TeleNetClient(TOKEN)
router = Router()

@router.on(Command("start"))
async def start(ctx):
    await bot.send_message(ctx.chat.id, "سلام! خوش اومدی 😎")

async def main():
    await bot.start()
    await bot.poll_updates(router=router)

if __name__ == "__main__":
    asyncio.run(main())
```


---

🔹 هندلرهای پیشرفته

```python
import asyncio
from telenet import TeleNetClient, Router, Command, InlineButton

TOKEN = "<YOUR_BOT_TOKEN>"
bot = TeleNetClient(TOKEN)
router = Router()

@router.on(Command("start"))
async def start(ctx):
    buttons = [
        [InlineButton("رفتن به گوگل", url="https://google.com"),
         InlineButton("رفتن به تلگرام", url="https://t.me")],
    ]
    await bot.send_message(
        ctx.chat.id,
        "یکی از گزینه‌ها را انتخاب کنید:",
        buttons=buttons
    )

async def main():
    await bot.start()
    await bot.poll_updates(router=router)

if __name__ == "__main__":
    asyncio.run(main())
```


---

## 🔹 ویژگی‌های پیشرفته

- کامند داینامیک: می‌توانی دستورها را در زمان اجرا اضافه یا حذف کنی.

- پشتیبانی از چندین Router: مدیریت پیچیده مسیرها و گروه‌های کامندها.

- سازگار با انواع آپدیت‌ها: پیام، عکس، فایل، استیکر و دکمه‌ها.

- ماژولار و قابل گسترش: افزودن Middleware و Hookهای اختصاصی آسان است.



---

## 🔹 نکات مهم

- ذخیره فایل‌ها با UTF-8 برای پیام‌های فارسی

- اجرای asyncio.run(main()) تنها یکبار در برنامه

- هندلرها باید async باشند

- برای پاسخ سریع‌تر، می‌توان از task‌های جداگانه استفاده کرد



---

🔹 مثال کامل ربات

i```python
import asyncio
from telenet import TeleNetClient, Router, Command, InlineButton

TOKEN = "<YOUR_BOT_TOKEN>"
bot = TeleNetClient(TOKEN)
router = Router()

@router.on(Command("start"))
async def start(ctx):
    # پیام خوش آمد
    await bot.send_message(ctx.chat.id, "سلام! خوش اومدی 😎")
    
    # پیام با دکمه‌های inline
    buttons = [
        [InlineButton("رفتن به گوگل", url="https://google.com"),
         InlineButton("رفتن به تلگرام", url="https://t.me")],
    ]
    await bot.send_message(
        ctx.chat.id,
        "یکی از گزینه‌ها را انتخاب کنید:",
        buttons=buttons
    )

async def main():
    await bot.start()
    await bot.poll_updates(router=router)

if __name__ == "__main__":
    asyncio.run(main())
```


---


🔹 چرا TeleNet؟

- ساده و سریع

- قابل گسترش و ماژولار

- مناسب برای ربات‌های حرفه‌ای و پروژه‌های بزرگ

- ساختار مدرن asyncio و مدیریت آسان کامندها


> Designed by Ali-Jafari & GPT | With ❤.
