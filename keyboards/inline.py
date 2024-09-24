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

# Кнопка "Хорошо"
start_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅",
                callback_data="ok"
            )
        ],
    ]
)

diseases = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Есть",
                callback_data="есть"
            )
        ],
        [
            InlineKeyboardButton(
                text="Нету",
                callback_data="нету"
            )
        ],
    ]
)