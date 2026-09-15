from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Daily Plan"), KeyboardButton(text="📊 Progress")],
            [KeyboardButton(text="📚 Vocabulary Recall"), KeyboardButton(text="❌ Error Factory")]
        ],
        resize_keyboard=True
    )

def vocab_inline_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Tarjimani ko'rish", callback_data="show_vocab_answer")]
    ])

def vocab_grade_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Qiyin", callback_data="grade_hard"),
            InlineKeyboardButton(text="🟡 O'rtacha", callback_data="grade_mid"),
            InlineKeyboardButton(text="🟢 Oson", callback_data="grade_easy")
        ]
    ])
