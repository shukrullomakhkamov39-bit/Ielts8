from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# AI servislaringizni shu yerda import qilasiz:
# from services.writing_ai import evaluate_essay
# from services.speaking_ai import evaluate_speech

router = Router()

# 1. Writing AI
@router.message(F.text == "✍️ Writing AI")
async def writing_ai_handler(message: Message):
    await message.answer(
        "✍️ **IELTS Writing AI Coach**\n\n"
        "IELTS Writing Task 1 yoki Task 2 inshoingizni (essay) matn shaklida yuboring. "
        "AI uni 4 ta mezon bo'yicha baholab, tavsiyalar beradi."
    )

# 2. Speaking AI
@router.message(F.text == "🗣️ Speaking AI")
async def speaking_ai_handler(message: Message):
    await message.answer(
        "🗣️ **IELTS Speaking AI Coach**\n\n"
        "Javobingizni ovozli xabar (**voice message**) shaklida yuboring. "
        "AI talaffuz, lug'at boyligi va grammatikani tekshiradi."
    )

# 3. Reading AI
@router.message(F.text == "📖 Reading AI")
async def reading_ai_handler(message: Message):
    await message.answer(
        "📖 **Reading AI Assistant**\n\n"
        "Tushunarsiz bo'lgan Reading matnini yoki qiyin savolni yuboring. "
        "AI uni tahlil qilib, to'g'ri javob kalitlarini tushuntirib beradi."
    )

# 4. Listening AI
@router.message(F.text == "🎧 Listening AI")
async def listening_ai_handler(message: Message):
    await message.answer(
        "🎧 **Listening AI Practice**\n\n"
        "Listening transkriptini yoki audio bo'yicha tushunmagan savolingizni yuboring. "
        "AI iboralar va parafrazalarni ajratib beradi."
    )

# 5. Grammar AI
@router.message(F.text == "📝 Grammar AI")
async def grammar_ai_handler(message: Message):
    await message.answer(
        "📝 **Grammar Checker AI**\n\n"
        "Grammatikasini tekshirmoqchi bo'lgan istalgan inglizcha matn yoki gapingizni yuboring. "
        "AI xatolaringizni to'g'rilab, qoidasini izohlaydi."
    )