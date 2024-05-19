from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Анализ")],
        [KeyboardButton(text="Ссылки")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Чего желаете?",
    selective=True,
)


cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отменить запрос")]],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)
