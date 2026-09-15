from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

scheduler = AsyncIOScheduler()

async def send_daily_reminder(bot: Bot, user_id: int):
    text = (
        "⏰ **IELTS COACH — KUNLIK ESLATMA**\n\n"
        "Bugungi mashg'ulotlarni boshlash vaqti keldi!\n"
        "Kunlik rejangizni ko'rish uchun 🎯 Daily Plan tugmasini bosing."
    )
    try:
        await bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
    except Exception:
        pass

def setup_scheduler(bot: Bot):
    # Har kuni ertalab soat 09:00 da eslatma
    scheduler.add_job(send_daily_reminder, "cron", hour=9, minute=0, args=[bot, 12345678])
    scheduler.start()