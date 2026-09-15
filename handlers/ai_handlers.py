from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# 1. AI Holatlarini (States) belgilash
class AIStates(StatesGroup):
    waiting_for_writing = State()
    waiting_for_speaking = State()
    waiting_for_reading = State()
    waiting_for_listening = State()
    waiting_for_grammar = State()

router = Router()

# ==================== READING AI ====================
@router.message(F.text == "📖 Reading AI")
async def reading_ai_start(message: Message, state: FSMContext):
    await state.set_state(AIStates.waiting_for_reading)  # Bot foydalanuvchini matn kutilayotgan holatga o'tkazadi
    await message.answer(
        "📖 **Reading AI Assistant**\n\n"
        "Tushunarsiz bo'lgan Reading matnini yoki qiyin savolni yuboring. AI uni tahlil qilib beradi."
    )

@router.message(AIStates.waiting_for_reading)
async def process_reading(message: Message, state: FSMContext):
    user_text = message.text
    await message.answer("⏳ *Reading AI matningizni tahlil qilmoqda...*")
    
    # Shu yerda AI servisingizni chaqirasiz (masalan: response = await ask_reading_ai(user_text))
    await message.answer(f"🤖 **Reading AI Tahlili:**\n\nSiz yuborgan matn: {user_text}\n\n(Bu yerda AI tahlil javobi bo'ladi)")
    await state.clear()  # Holatni yakunlash


# ==================== GRAMMAR AI ====================
@router.message(F.text == "📝 Grammar AI")
async def grammar_ai_start(message: Message, state: FSMContext):
    await state.set_state(AIStates.waiting_for_grammar)
    await message.answer("📝 **Grammar AI**: Grammatikasini tekshirmoqchi bo'lgan matningizni yuboring:")

@router.message(AIStates.waiting_for_grammar)
async def process_grammar(message: Message, state: FSMContext):
    user_text = message.text
    await message.answer("⏳ *Grammatika tekshirilmoqda...*")
    
    await message.answer(f"📝 **Grammar AI Natijasi:**\n\nMatn: '{user_text}' - Grammatik jihatdan to'g'ri!")
    await state.clear()


# ==================== WRITING AI ====================
@router.message(F.text == "✍️ Writing AI")
async def writing_ai_start(message: Message, state: FSMContext):
    await state.set_state(AIStates.waiting_for_writing)
    await message.answer("✍️ **Writing AI**: IELTS Essayingizni yuboring:")

@router.message(AIStates.waiting_for_writing)
async def process_writing(message: Message, state: FSMContext):
    # from services.writing_ai import evaluate_essay
    await message.answer("✍️ *Writing inshoingiz tahlil qilinmoqda...*")
    await state.clear()


# ==================== LISTENING AI ====================
@router.message(F.text == "🎧 Listening AI")
async def listening_ai_start(message: Message, state: FSMContext):
    await state.set_state(AIStates.waiting_for_listening)
    await message.answer("🎧 **Listening AI**: Transkript yoki savolingizni yuboring:")

@router.message(AIStates.waiting_for_listening)
async def process_listening(message: Message, state: FSMContext):
    await message.answer("🎧 *Listening material tahlil qilinmoqda...*")
    await state.clear()


# ==================== SPEAKING AI ====================
@router.message(F.text == "🗣️ Speaking AI")
async def speaking_ai_start(message: Message, state: FSMContext):
    await state.set_state(AIStates.waiting_for_speaking)
    await message.answer("🗣️ **Speaking AI**: Ovozli xabaringizni (voice) yuboring:")

@router.message(AIStates.waiting_for_speaking)
async def process_speaking(message: Message, state: FSMContext):
    await message.answer("🗣️ *Ovozli xabaringiz tahlil qilinmoqda...*")
    await state.clear()