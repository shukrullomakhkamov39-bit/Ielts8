from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from writing_ai import evaluate_essay
from speaking_ai import evaluate_speech

router = Router()

class EssayState(StatesGroup):
    waiting_for_essay = State()

# 1. Writing Check (Matnli insho baholash)
@router.message(F.text == "✍️ Writing Check")
async def ask_essay(message: Message, state: FSMContext):
    await message.answer("✍️ **Writing Task 1 yoki Task 2 insho matnini yuboring:**")
    await state.set_state(EssayState.waiting_for_essay)

@router.message(EssayState.waiting_for_essay)
async def process_essay(message: Message, state: FSMContext):
    await message.answer("🧠 **AI Inshoni tahlil qilmoqda, biroz kuting...**")
    feedback = await evaluate_essay(message.text)
    await message.answer(feedback, parse_mode="Markdown")
    await state.clear()

# 2. Speaking Check (Ovozli xabarni avtomatik baholash)
@router.message(F.voice)
async def process_voice(message: Message, bot: Bot):
    await message.answer("🎙 **Ovozli xabaringiz AI (Whisper + GPT-4o) orqali tahlil qilinmoqda...**")
    
    file_info = await bot.get_file(message.voice.file_id)
    file_path = f"voice_{message.from_user.id}.ogg"
    await bot.download_file(file_info.file_path, file_path)
    
    feedback = await evaluate_speech(file_path)
    await message.answer(feedback, parse_mode="Markdown")