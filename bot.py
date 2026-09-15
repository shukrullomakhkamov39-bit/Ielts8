import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://example.com")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Rejalashtirgichni ochish (Mini App)", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="📊 Mening statistikalarim"), KeyboardButton(text="📝 Bugungi vazifalar")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 **Shaxsiy Maqsad va Odatlar Rejalashtirgichiga xush kelibsiz!**\n\n"
        "Quyidagi **'Rejalashtirgichni ochish'** tugmasi orqali interaktiv Mini App-ni ochishingiz yoki bot menyusidan foydalanishingiz mumkin:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "📊 Mening statistikalarim")
async def stats_cmd(message: types.Message):
    await message.answer(
        "📊 **Sizning Statistikangiz:**\n\n"
        "✨ Bajarilgan xohishlar: **12 / 100**\n"
        "🎯 Oylik maqsadlar bajarilishi: **65%**\n"
        "🔥 Ketma-ket bajarilgan odatlar: **7 kun**\n\n"
        "To'liqroq va qulayroq interfeys uchun Mini App-dan foydalaning!"
    )

@dp.message(F.text == "📝 Bugungi vazifalar")
async def today_tasks(message: types.Message):
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Kitob o'qish (20 bet)", callback_data="task_done_1")],
            [InlineKeyboardButton(text="✅ 30 daqiqa sport", callback_data="task_done_2")],
            [InlineKeyboardButton(text="➕ Yangi vazifa qo'shish", callback_data="add_task")]
        ]
    )
    await message.answer("📌 **Bugungi rejalashtirilgan vazifalar:**", reply_markup=inline_kb)

@dp.callback_query(F.data.startswith("task_done_"))
async def process_task_done(callback: types.CallbackQuery):
    await callback.answer("Vazifa bajarildi deb belgilandi! 🎉", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
