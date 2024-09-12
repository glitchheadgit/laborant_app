import io
import pandas as pd

from io import StringIO

from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from config_reader import config
from utils.states import Form
from utils.model import retrieve_table_from_text, analyze_table_with_gpt
from utils.preprocessing import save_data
from utils.preprocessing_1 import read_document
from keyboards import reply

router = Router()

# Шаг 1: Ожидание загрузки PDF
@router.message(F.text.in_(["/analysis", "Расшифровать анализ"]))
async def get_photo(message: Message, state: FSMContext):
    await state.set_state(Form.user_analyses)
    await message.answer("Пожалуйста, загрузите <b>PDF</b> документ с результатами анализов", reply_markup=reply.cancel)

# Шаг 2: Обработка PDF
@router.message(Form.user_analyses, F.document.file_name.endswith('.pdf'))
async def process_pdf(message: Message, state: FSMContext):
    await message.answer(
        '📝 Мы получили Ваши анализы и приступили к обработке.\n\n⏳ Это займет не более 3 минут.',
    )
    file_id = message.document.file_id
    file = await message.bot.download(file_id)
    text = read_document(file)

    # Извлечение данных из состояния пользователя
    user_data = await state.get_data()
    table_text, table_text_deviation = retrieve_table_from_text(text)

    # Шаг 3: Вывод расшифрованной таблицы и вопрос о корректности
    await state.update_data(table_text=table_text)
    await ask_for_table_verification(message, table_text)

# Шаг 3.1: Функция для вывода таблицы и кнопок
async def ask_for_table_verification(message: Message, table_text: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="correct_table")],
        [InlineKeyboardButton(text="Нет", callback_data="incorrect_table")]
    ])
    await message.answer(
        f"Расшифрованная таблица:\n\n<pre><code>{table_text}</code></pre>\n\nПравильно ли расшифрованы показатели?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Шаг 4: Обработка ответа пользователя на корректность таблицы
@router.callback_query(F.data == "correct_table")
async def table_correct(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Отлично! Продолжаем обработку.")
    
    # Извлекаем данные из состояния
    data = await state.get_data()
    table_text = data['table_text']
    
    # Формируем запрос для GPT-4 и продолжаем процесс
    user_data = await state.get_data()
    formatter = {'age': user_data['age'], 'sex': user_data['sex'], 'table_text': table_text, 'table_text_deviation': ""}
    prompt = config.prompt.get_secret_value().format(**formatter)
    analyses = analyze_table_with_gpt(prompt)
    
    # Сохранение данных
    save_data(call.message.chat.id, user_data['age'], user_data['sex'], table_text, analyses)

    await call.message.answer("Анализ завершен.")
    await call.answer()

@router.callback_query(F.data == "incorrect_table")
async def table_incorrect(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Укажите, пожалуйста, названия показателей, которые расшифрованы неверно.")
    await state.set_state(Form.incorrect_table_names)

# Шаг 5: Ввод неверных показателей
@router.message(Form.incorrect_table_names)
async def incorrect_table_names(message: Message, state: FSMContext):
    incorrect_names = message.text.split(",")  # Предполагаем, что пользователь вводит через запятую
    await state.update_data(incorrect_names=incorrect_names)
    await message.answer("Укажите правильные показатели для каждого неверного показателя через точку.")
    await state.set_state(Form.correct_table_values)

# Шаг 6: Ввод правильных значений для неверных показателей
@router.message(Form.correct_table_values)
async def correct_table_values(message: Message, state: FSMContext):
    correct_values = message.text.split(",")  # Правильные значения через запятую с точкой как разделитель
    data = await state.get_data()
    incorrect_names = data['incorrect_names']

    # Шаг 7: Обновление таблицы
    table_text = data['table_text']
    table_lines = table_text.split("\n")
    updated_lines = []

    for line in table_lines:
        for incorrect, correct in zip(incorrect_names, correct_values):
            if incorrect in line:
                line = line.replace(incorrect, correct)
        updated_lines.append(line)

    updated_table = "\n".join(updated_lines)

    # Сохранение обновленной таблицы и продолжение обработки
    await state.update_data(table_text=updated_table)
    await message.answer("Таблица обновлена. Продолжаем обработку.")
    
    # Запускаем обработку заново с обновленной таблицей
    await ask_for_table_verification(message, updated_table)
