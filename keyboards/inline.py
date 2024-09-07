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

# Основное меню (пример)
main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Начать новый анализ",
                callback_data="start_analysis"
            )
        ]
    ]
)