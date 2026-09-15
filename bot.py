import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash (local muhit uchun)
load_dotenv()

# Loglarni formatlash va sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Telegram Bot Tokenini tekshirish
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("CRITICAL: BOT_TOKEN environment o'zgaruvchisi topilmadi!")

# Handler routerlarini import qilish
from handlers import onboarding, dashboard, writing, ai_handlers


async def main():
    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Dispatcherga barcha handler routerlarini ulash
    dp.include_router(onboarding.router)
    dp.include_router(dashboard.router)
    dp.include_router(writing.router)
    dp.include_router(ai_handlers.router)

    # Bot o'chiq vaqtidagi eski kelgan xabarlarni o'chirib tashlash (Conflict error oldini oladi)
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("🚀 IELTS Coach Bot muvaffaqiyatli ishga tushdi!")
    
    # Pollingni boshlash
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot to'xtatildi.")