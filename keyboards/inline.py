from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Оплатить", callback_data="start_payment"))
    return builder.as_markup()


def create_file_rating(file_id):
    rating = InlineKeyboardBuilder()
    rating.row(
        InlineKeyboardButton(
            text="👎",
            callback_data=f"rating_{file_id}_0"
            ),
        InlineKeyboardButton(
            text="👍",
            callback_data=f"rating_{file_id}_1"
            )
    )

    return rating.as_markup()

    
sex = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Мужской",
                callback_data="мужской"
            )
        ],
        [
            InlineKeyboardButton(
                text="Женский",
                callback_data="женский"
            )
        ],
    ]
)

# Кнопка "Хорошо"
start_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅",
                callback_data="policy_confirmed"
            )
        ],
    ]
)

diseases = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Есть",
                callback_data="F"
            )
        ],
        [
            InlineKeyboardButton(
                text="Нет",
                callback_data="T"
            )
        ],
    ]
)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def get_payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Оплатить", callback_data="start_payment"))
    return builder.as_markup()
