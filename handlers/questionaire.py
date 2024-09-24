import io
import re
import pandas as pd

from io import StringIO

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from config_reader import config
from utils.states import Form
from utils.model import retrieve_table_from_text, analyze_table_with_gpt, getting_bioethic_response
from utils.preprocessing import read_pdf, save_data
from utils.preprocessing_1 import read_document
from keyboards import reply


router = Router()

@router.message(Form.user_analyses, F.document.file_name.endswith('.pdf'))
async def process_pdf(message: Message, state: FSMContext):
    await message.answer(
        '📝 Мы получили Ваши анализы и приступили к обработке.\n\n⏳ Это займет не более 3 минут.',
    )
    file_id = message.document.file_id
    #try:
    # Загрузка и чтение PDF
    file = await message.bot.download(file_id)
    text = read_pdf(file)
    
    # Извлечение данных из состояния пользователя
    user_data = await state.get_data()
    table_text, table_text_deviation = retrieve_table_from_text(text)
    
    # Формирование запроса для GPT-4
    formatter = {'age': user_data['age'], 'sex': user_data['sex'], 'table_text': table_text, 'table_text_deviation': table_text_deviation, 'diseases': user_data['diseases']}
    prompt = config.prompt.get_secret_value().format(**formatter)
    analyses = analyze_table_with_gpt(prompt)
    bioethic_response = getting_bioethic_response(analyses)
    # Сохранение данных
    save_data(message.chat.id, user_data['age'], user_data['sex'], table_text, analyses)

    # Отладка: выводим содержимое исходной таблицы
    # await message.reply(
    #     f"Исходная расшифрованная таблица:\n\n<pre><code>{table_text}</code></pre>",
    #     reply_markup=reply.main,
    #     parse_mode="HTML"
    # )

    # Пробуем преобразовать текст в DataFrame
    try:
        df = pd.read_csv(StringIO(table_text))
        # await message.reply(f"Столбцы таблицы: {', '.join(df.columns)}", reply_markup=reply.main)
    except Exception as e:
        pass # await message.reply(f"Ошибка при создании DataFrame: {str(e)}", reply_markup=reply.main)

    # Форматирование анализа и отклонений для вывода
    result = re.sub(r'<([^>]*)\n', r'&lt;\1', bioethic_response.replace('&', '&amp'))
    result = re.sub(r'\n([^<]*)>', r'\1&gt;', result)

    # Разделяем текст на предсказания и рекоммендации
    anal, rec = result.split('На основе результатов ваших анализов мы рекомендуем следующие дополнительные исследования')
    rec = 'На основе результатов ваших анализов мы рекомендуем следующие дополнительные исследования' + rec

    await message.reply(
        f"{anal}",
        parse_mode="HTML"
    )
    # Вывод результата анализа
    await message.reply(
        f"{rec}",
        parse_mode="HTML"
    )
   #  except Exception as e:
    #    await message.reply(
     #       f"<pre><code>Ошибка: {str(e).replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;')}</code></pre>",
      #      reply_markup=reply.main,
       #     parse_mode="HTML"
        #)


@router.message(Form.user_analyses, F.document.file_name.regexp('.*docx?'))
async def process_docx(message: Message, state: FSMContext):
    await message.answer(
            'Подождите минуту, Ваши анализы обрабатываются...',
    )
    file_id = message.document.file_id
    try:
        file = await message.bot.download(file_id)
        text = read_docx(file)
        table_text, table_text_deviation = retrieve_table_from_text(text)
        formatter = {'age': user_data['age'], 'sex': user_data['sex'], 'table_text': table_text, 'table_text_deviation': table_text_deviation, 'diseases': user_data['diseases']}
        prompt = config.prompt.get_secret_value().format(**formatter)
        analyses = analyze_table_with_gpt(prompt)
        #тут добавил переменную и после нее в резалт теперь биоэтик респонс
        bioethic_response = getting_bioethic_response(analyses)
        save_data(message.chat.id, user_data['age'], user_data['sex'], table_text, analyses)
        result = re.sub(r'<([^>]*)\n', r'&lt;\1', bioethic_response.replace('&', '&amp'))
        result = re.sub(r'\n([^<]*)>', r'\1&gt;', result)

        # Разделяем текст на предсказания и рекоммендации
        anal, rec = result.split('На основе результатов ваших анализов мы рекомендуем следующие дополнительные исследования')
        rec = 'На основе результатов ваших анализов мы рекомендуем следующие дополнительные исследования' + rec

        await message.reply(
            f"{anal}",
            parse_mode="HTML"
        )
        # Вывод результата анализа
        await message.reply(
            f"{rec}",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply(
            '<pre><code>' + str(e).replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;') + '</code></pre>',
        )

@router.message(Form.user_analyses, ~F.document.file_name.regexp(r'.*.pdf|.*.docx?'))
async def wrong_format_handler(message: Message, state: FSMContext):
    if message.text == "Отменить запрос":
        await state.clear()
        await message.answer("Готов к работе!")
    else:
        await message.answer("Отправьте <b>документ</b> в формате <b>pdf</b>!")
