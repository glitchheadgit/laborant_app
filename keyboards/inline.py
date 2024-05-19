from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


links = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Код проекта",
                url="https://github.com/glitchheadgit/laborant_app",
            )
        ],
    ]
)
