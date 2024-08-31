from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
