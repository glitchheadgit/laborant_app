from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отменить запрос")]],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
    input_field_placeholder='Следуйте инструкциям',
)

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Расшифровать анализ")],
        [KeyboardButton(text="Обратная связь")],
        [KeyboardButton(text="О нас")],
        #[KeyboardButton(text="FAQ")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    selective=True,
    input_field_placeholder='Выберите команду',
)
