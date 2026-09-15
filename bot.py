import os
import asyncio
import logging
import sqlite3
from datetime import datetime, date, timedelta

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

# ============================================================
# CONFIG
# ============================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://example.com")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. .env faylga BOT_TOKEN=... yozing."
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_NAME = "planner.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Goals
    cur.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # Tasks
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            task_date TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # Habits
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Habit logs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            telegram_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            UNIQUE(habit_id, log_date)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# USER
# ============================================================

def save_user(user: types.User):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (
            telegram_id,
            username,
            first_name,
            created_at
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(telegram_id)
        DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name
    """, (
        user.id,
        user.username,
        user.first_name,
        datetime.now().isoformat(),
    ))

    conn.commit()
    conn.close()


# ============================================================
# KEYBOARDS
# ============================================================

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 Rejalashtirgichni ochish",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ],
            [
                KeyboardButton(text="📊 Mening statistikalarim"),
                KeyboardButton(text="📝 Bugungi vazifalar"),
            ],
            [
                KeyboardButton(text="🎯 Maqsadlarim"),
                KeyboardButton(text="🔥 Odatlarim"),
            ],
            [
                KeyboardButton(text="➕ Vazifa qo‘shish"),
                KeyboardButton(text="➕ Maqsad qo‘shish"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Bosh menyu",
                    callback_data="back_home",
                )
            ]
        ]
    )


# ============================================================
# /START
# ============================================================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):

    save_user(message.from_user)

    await message.answer(
        f"👋 Assalomu alaykum, "
        f"<b>{message.from_user.first_name}</b>!\n\n"
        "🧠 <b>Shaxsiy Maqsad va Odatlar Rejalashtirgichi</b>\n\n"
        "Bu bot orqali:\n"
        "🎯 maqsadlaringizni boshqarishingiz\n"
        "📝 kundalik vazifalarni rejalashtirishingiz\n"
        "🔥 odatlaringizni kuzatishingiz\n"
        "📊 statistikangizni ko‘rishingiz mumkin.\n\n"
        "📱 Mini App orqali to‘liq interfeysni ochishingiz mumkin.",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )


# ============================================================
# TODAY TASKS
# ============================================================

@dp.message(F.text == "📝 Bugungi vazifalar")
async def today_tasks(message: types.Message):

    save_user(message.from_user)

    today = date.today().isoformat()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM tasks
        WHERE telegram_id = ?
        AND task_date = ?
        ORDER BY completed ASC, id DESC
    """, (message.from_user.id, today))

    tasks = cur.fetchall()
    conn.close()

    if not tasks:
        await message.answer(
            "📭 <b>Bugun uchun vazifalar yo‘q.</b>\n\n"
            "➕ Vazifa qo‘shish tugmasidan foydalaning.",
            parse_mode="HTML",
        )
        return

    buttons = []

    text = "📝 <b>Bugungi vazifalar</b>\n\n"

    for i, task in enumerate(tasks, start=1):

        status = "✅" if task["completed"] else "⬜"

        text += (
            f"{status} <b>{i}.</b> "
            f"{task['title']}\n"
        )

        if not task["completed"]:
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {task['title'][:30]}",
                    callback_data=f"task_done:{task['id']}",
                )
            ])

    buttons.append([
        InlineKeyboardButton(
            text="🔄 Yangilash",
            callback_data="refresh_tasks",
        )
    ])

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        ),
        parse_mode="HTML",
    )


# ============================================================
# COMPLETE TASK
# ============================================================

@dp.callback_query(F.data.startswith("task_done:"))
async def process_task_done(callback: types.CallbackQuery):

    task_id = int(callback.data.split(":")[1])

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        AND telegram_id = ?
    """, (task_id, callback.from_user.id))

    conn.commit()

    updated = cur.rowcount

    conn.close()

    if updated:
        await callback.answer(
            "🎉 Vazifa bajarildi!",
            show_alert=True,
        )
    else:
        await callback.answer(
            "❌ Vazifa topilmadi.",
            show_alert=True,
        )

    await callback.message.delete()

    # qayta chiqarish
    await today_tasks(callback.message)


# ============================================================
# REFRESH TASKS
# ============================================================

@dp.callback_query(F.data == "refresh_tasks")
async def refresh_tasks(callback: types.CallbackQuery):

    await callback.message.delete()

    await today_tasks(callback.message)

    await callback.answer("Yangilandi 🔄")


# ============================================================
# ADD TASK BUTTON
# ============================================================

@dp.message(F.text == "➕ Vazifa qo‘shish")
async def add_task_start(message: types.Message):

    await message.answer(
        "➕ <b>Yangi vazifa</b>\n\n"
        "Vazifa nomini yozing.\n\n"
        "Masalan:\n"
        "<code>30 daqiqa English o‘rganish</code>",
        parse_mode="HTML",
    )

    # simple state alternative
    dp["waiting_task"] = message.from_user.id


@dp.message()
async def catch_text(message: types.Message):

    user_id = message.from_user.id

    # ==========================================
    # ADD TASK
    # ==========================================

    if dp.get("waiting_task") == user_id:

        title = message.text.strip()

        if len(title) < 2:
            await message.answer(
                "❌ Vazifa nomi juda qisqa."
            )
            return

        today = date.today().isoformat()

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO tasks (
                telegram_id,
                title,
                task_date,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            title,
            today,
            datetime.now().isoformat(),
        ))

        conn.commit()
        conn.close()

        dp["waiting_task"] = None

        await message.answer(
            f"✅ <b>Vazifa qo‘shildi!</b>\n\n"
            f"📝 {title}\n"
            f"📅 Bugun",
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )


# ============================================================
# STATISTICS
# ============================================================

@dp.message(F.text == "📊 Mening statistikalarim")
async def stats_cmd(message: types.Message):

    user_id = message.from_user.id

    conn = get_db()
    cur = conn.cursor()

    # Total tasks
    cur.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE telegram_id = ?
    """, (user_id,))

    total_tasks = cur.fetchone()[0]

    # Completed tasks
    cur.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE telegram_id = ?
        AND completed = 1
    """, (user_id,))

    completed_tasks = cur.fetchone()[0]

    # Goals
    cur.execute("""
        SELECT COUNT(*)
        FROM goals
        WHERE telegram_id = ?
    """, (user_id,))

    total_goals = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM goals
        WHERE telegram_id = ?
        AND completed = 1
    """, (user_id,))

    completed_goals = cur.fetchone()[0]

    # Habits
    cur.execute("""
        SELECT COUNT(*)
        FROM habits
        WHERE telegram_id = ?
    """, (user_id,))

    habits = cur.fetchone()[0]

    conn.close()

    task_percent = (
        round(completed_tasks / total_tasks * 100)
        if total_tasks
        else 0
    )

    goal_percent = (
        round(completed_goals / total_goals * 100)
        if total_goals
        else 0
    )

    await message.answer(
        "📊 <b>Sizning statistikangiz</b>\n\n"
        f"📝 Vazifalar: "
        f"<b>{completed_tasks}/{total_tasks}</b>\n"
        f"📈 Vazifalar bajarilishi: <b>{task_percent}%</b>\n\n"
        f"🎯 Maqsadlar: "
        f"<b>{completed_goals}/{total_goals}</b>\n"
        f"📈 Maqsadlar bajarilishi: <b>{goal_percent}%</b>\n\n"
        f"🔥 Odatlar: <b>{habits}</b>\n\n"
        "💡 Davom eting — kichik qadamlar katta natija beradi!",
        parse_mode="HTML",
    )


# ============================================================
# GOALS
# ============================================================

@dp.message(F.text == "🎯 Maqsadlarim")
async def my_goals(message: types.Message):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM goals
        WHERE telegram_id = ?
        ORDER BY completed ASC, id DESC
    """, (message.from_user.id,))

    goals = cur.fetchall()
    conn.close()

    if not goals:
        await message.answer(
            "🎯 <b>Hali maqsadlaringiz yo‘q.</b>\n\n"
            "➕ Maqsad qo‘shish tugmasidan foydalaning.",
            parse_mode="HTML",
        )
        return

    text = "🎯 <b>Maqsadlarim</b>\n\n"
    buttons = []

    for goal in goals:

        status = "✅" if goal["completed"] else "🎯"

        text += (
            f"{status} <b>{goal['title']}</b>\n"
        )

        if goal["deadline"]:
            text += f"📅 Deadline: {goal['deadline']}\n"

        text += "\n"

        if not goal["completed"]:
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {goal['title'][:30]}",
                    callback_data=f"goal_done:{goal['id']}",
                )
            ])

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        ) if buttons else None,
        parse_mode="HTML",
    )


# ============================================================
# COMPLETE GOAL
# ============================================================

@dp.callback_query(F.data.startswith("goal_done:"))
async def goal_done(callback: types.CallbackQuery):

    goal_id = int(callback.data.split(":")[1])

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE goals
        SET completed = 1
        WHERE id = ?
        AND telegram_id = ?
    """, (
        goal_id,
        callback.from_user.id,
    ))

    conn.commit()
    conn.close()

    await callback.answer(
        "🎯 Maqsad bajarildi! 🔥",
        show_alert=True,
    )

    await callback.message.delete()


# ============================================================
# ADD GOAL
# ============================================================

@dp.message(F.text == "➕ Maqsad qo‘shish")
async def add_goal_start(message: types.Message):

    dp["waiting_goal"] = message.from_user.id

    await message.answer(
        "🎯 <b>Yangi maqsad</b>\n\n"
        "Maqsadingizni yozing.\n\n"
        "Masalan:\n"
        "<code>IELTS 7.5 olish</code>",
        parse_mode="HTML",
    )


# ============================================================
# HABITS
# ============================================================

@dp.message(F.text == "🔥 Odatlarim")
async def my_habits(message: types.Message):

    user_id = message.from_user.id
    today = date.today().isoformat()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM habits
        WHERE telegram_id = ?
        ORDER BY id DESC
    """, (user_id,))

    habits = cur.fetchall()

    if not habits:
        conn.close()

        await message.answer(
            "🔥 <b>Hali odatlar yo‘q.</b>\n\n"
            "Mini App orqali odat qo‘shishingiz mumkin.",
            parse_mode="HTML",
        )
        return

    text = "🔥 <b>Bugungi odatlar</b>\n\n"
    buttons = []

    for habit in habits:

        cur.execute("""
            SELECT id
            FROM habit_logs
            WHERE habit_id = ?
            AND telegram_id = ?
            AND log_date = ?
        """, (
            habit["id"],
            user_id,
            today,
        ))

        done = cur.fetchone()

        status = "✅" if done else "⬜"

        text += f"{status} {habit['title']}\n"

        if not done:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🔥 {habit['title'][:30]}",
                    callback_data=f"habit_done:{habit['id']}",
                )
            ])

    conn.close()

    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        ) if buttons else None,
        parse_mode="HTML",
    )


# ============================================================
# COMPLETE HABIT
# ============================================================

@dp.callback_query(F.data.startswith("habit_done:"))
async def habit_done(callback: types.CallbackQuery):

    habit_id = int(callback.data.split(":")[1])
    today = date.today().isoformat()

    conn = get_db()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO habit_logs (
                habit_id,
                telegram_id,
                log_date
            )
            VALUES (?, ?, ?)
        """, (
            habit_id,
            callback.from_user.id,
            today,
        ))

        conn.commit()

        await callback.answer(
            "🔥 Odat bajarildi! Zo‘r! 💪",
            show_alert=True,
        )

    except sqlite3.IntegrityError:

        await callback.answer(
            "Bu odat bugun allaqachon bajarilgan.",
            show_alert=True,
        )

    finally:
        conn.close()

    await callback.message.delete()


# ============================================================
# ADD GOAL/TASK FROM TEXT HANDLER
# ============================================================

@dp.message()
async def text_input_handler(message: types.Message):

    user_id = message.from_user.id

    # Goal
    if dp.get("waiting_goal") == user_id:

        title = message.text.strip()

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO goals (
                telegram_id,
                title,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            user_id,
            title,
            datetime.now().isoformat(),
        ))

        conn.commit()
        conn.close()

        dp["waiting_goal"] = None

        await message.answer(
            "🎯 <b>Maqsad qo‘shildi!</b>\n\n"
            f"🚀 {title}",
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )


# ============================================================
# BACK HOME
# ============================================================

@dp.callback_query(F.data == "back_home")
async def back_home(callback: types.CallbackQuery):

    await callback.message.delete()

    await callback.message.answer(
        "🏠 <b>Bosh menyu</b>",
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )

    await callback.answer()


# ============================================================
# WEB APP DATA
# ============================================================

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):

    try:

        data = message.web_app_data.data

        logging.info(
            "Mini App data: %s",
            data,
        )

        await message.answer(
            "✅ Mini App ma'lumotlari qabul qilindi!"
        )

    except Exception as e:

        logging.exception(
            "WebApp data error: %s",
            e,
        )


# ============================================================
# ERROR HANDLER
# ============================================================

@dp.errors()
async def error_handler(event):
    logging.exception(
        "Bot error: %s",
        event.exception,
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    init_db()

    logging.info("====================================")
    logging.info("Planner bot ishga tushmoqda...")
    logging.info("Mini App URL: %s", WEBAPP_URL)
    logging.info("Database: %s", DB_NAME)
    logging.info("====================================")

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logging.info("Bot to‘xtatildi.")

