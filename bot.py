import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import BOT_TOKEN
from database.db import init_db
from handlers import onboarding, dashboard

logging.basicConfig(level=logging.INFO)

async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN ko'rsatilmadi! .env faylini tekshiring.")

    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(onboarding.router)
    dp.include_router(dashboard.router)

    print("🚀 IELTS Coach Bot faol holatda ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
