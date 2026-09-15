from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from datetime import datetime
from database.db import async_session
from database.models import User
from keyboards.main import main_menu

router = Router()

class OnboardingState(StatesGroup):
    name = State()
    level = State()
    target = State()
    hours = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if user:
            await message.answer(
                f"Xush kelibsiz, **{user.name}**!\n6 oylik IELTS tayyorgarlik tizimi faol.",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
            return

    await message.answer(
        "🧠 **IELTS COACH SYSTEM**\n\n"
        "6 oylik individual IELTS 7.5+ tizimiga xush kelibsiz!\n"
        "Boshlash uchun ismingizni kiriting:",
        parse_mode="Markdown"
    )
    await state.set_state(OnboardingState.name)

@router.message(OnboardingState.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Hozirgi IELTS / ingliz tili darajangiz (masalan: A2, B1, B2):")
    await state.set_state(OnboardingState.level)

@router.message(OnboardingState.level)
async def process_level(message: Message, state: FSMContext):
    await state.update_data(level=message.text)
    await message.answer("Maqsadingiz bo'lgan Band score (masalan: 7.0, 7.5, 8.0):")
    await state.set_state(OnboardingState.target)

@router.message(OnboardingState.target)
async def process_target(message: Message, state: FSMContext):
    try:
        target = float(message.text)
        await state.update_data(target=target)
        await message.answer("Kuniga necha soat vaqt ajrata olasiz? (masalan: 3, 4.5):")
        await state.set_state(OnboardingState.hours)
    except ValueError:
        await message.answer("Iltimos, faqat raqam kiriting (masalan: 7.5):")

@router.message(OnboardingState.hours)
async def process_hours(message: Message, state: FSMContext):
    try:
        hours = float(message.text)
        data = await state.get_data()
        
        async with async_session() as session:
            new_user = User(
                telegram_id=message.from_user.id,
                name=data['name'],
                current_level=data['level'],
                target_band=data['target'],
                daily_hours=hours,
                start_date=datetime.utcnow()
            )
            session.add(new_user)
            await session.commit()

        await state.clear()
        await message.answer(
            "🎉 **Profil muvaffaqiyatli yaratildi!**\n"
            "180 kunlik shaxsiy rejagiz tuzildi.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("Iltimos, son kiriting (masalan: 4):")
