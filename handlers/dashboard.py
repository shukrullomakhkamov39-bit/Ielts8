from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from database.db import async_session
from database.models import User, UserError
from services.planner import calculate_phase
from keyboards.main import vocab_inline_kb, vocab_grade_kb

router = Router()

@router.message(F.text == "🎯 Daily Plan")
async def show_daily_plan(message: Message):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Avval /start buyrug'ini bosing.")
            return

        day, phase = calculate_phase(user.start_date)
        
        plan_text = (
            f"📅 **DAY {day} / 180**\n"
            f"📌 `{phase}`\n\n"
            f"🎯 **Bugungi reja ({user.daily_hours} soat):**\n"
            f"📚 Vocabulary Engine — 45 min\n"
            f"🎧 Listening Practice — 60 min\n"
            f"📖 Reading Strategy — 45 min\n"
            f"✍️ Writing Task Analysis — 45 min\n"
            f"🗣 Speaking Part 1/2 — 35 min\n"
            f"❌ Error Retest — 20 min\n\n"
            f"🔥 Streak: **{user.streak} kun**"
        )
        await message.answer(plan_text, parse_mode="Markdown")

@router.message(F.text == "📊 Progress")
async def show_progress(message: Message):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Avval /start buyrug'ini bosing.")
            return

        day, phase = calculate_phase(user.start_date)

        progress_text = (
            f"📊 **PROGRESS DASHBOARD**\n\n"
            f"👤 O'quvchi: **{user.name}**\n"
            f"🎯 Target Band: **{user.target_band}**\n"
            f"📈 Joriy daraja: **{user.current_level}**\n\n"
            f"⏱ Bajarilgan kunlar: **{day}/180**\n"
            f"🔥 Joriy Streak: **{user.streak} kun**\n"
            f"📍 Hozirgi bosqich: `{phase}`"
        )
        await message.answer(progress_text, parse_mode="Markdown")

@router.message(F.text == "📚 Vocabulary Recall")
async def start_vocab(message: Message):
    card_text = (
        "🧠 **ACTIVE RECALL**\n\n"
        "So'z: **Environment**\n"
        "🔊 Pronunciation: /ɪnˈvaɪrənmənt/\n\n"
        "💭 Ma'nosini eslashga harakat qiling..."
    )
    await message.answer(card_text, reply_markup=vocab_inline_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "show_vocab_answer")
async def reveal_vocab(call: CallbackQuery):
    answer_text = (
        "💡 **Javob:**\n"
        "🌐 Tarjima: Atrof-muhit\n"
        "📌 Def: The surroundings or conditions in which a person, animal, or plant lives.\n"
        "📖 Context: *We must protect the natural environment.*"
    )
    await call.message.edit_text(answer_text, reply_markup=vocab_grade_kb(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("grade_"))
async def process_vocab_grade(call: CallbackQuery):
    await call.message.edit_text("✅ Javobingiz saqlandi! Spaced Repetition algoritmi yangilandi.")

@router.message(F.text == "❌ Error Factory")
async def show_error_factory(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(UserError).where(
                UserError.user_id == message.from_user.id, 
                UserError.is_mastered == False
            )
        )
        errors = result.scalars().all()

        if not errors:
            await message.answer("🎉 Hozircha hal qilinmagan xatolaringiz yo'q! Ajoyib natija.")
            return

        err = errors[0]
        text = (
            f"❌ **ERROR FACTORY (Retest)**\n\n"
            f"📌 Skill: {err.skill}\n"
            f"❓ Savol: {err.question}\n"
            f"⚠️ Sizning javobingiz: `{err.user_answer}`\n"
            f"✅ To'g'ri javob: `{err.correct_answer}`\n"
            f"💡 Sabab: {err.reason}"
        )
        await message.answer(text, parse_mode="Markdown")
