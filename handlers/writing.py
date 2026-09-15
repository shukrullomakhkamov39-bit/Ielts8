from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from services.writing_ai import evaluate_essay

router = Router()

class EssayState(StatesGroup):
    waiting_for_essay = State()

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