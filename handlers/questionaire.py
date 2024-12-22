import io
import re
import bson
import pandas as pd

from io import StringIO

from aiogram.types import Message, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from utils.model import retrieve_table_from_text, analyze_table_with_gpt, getting_bioethic_response, diseases_check
from utils.preprocessing import read_pdf, read_docx
from utils.laborantdb import db_find_user_profile, db_create_file, db_analysis_inc
# from utils.preprocessing_1 import read_document
from config_reader import config
from utils.states import Form
from keyboards import reply
from keyboards.inline import create_file_rating


router = Router()

@router.message(Form.user_analyses, F.document.file_name.endswith('.pdf'))
async def process_pdf(message: Message, state: FSMContext):
    from bot import db
    await message.answer(
        '📝 Мы получили Ваши анализы и приступили к обработке.\n\n⏳ Это займет не более 3 минут.',
    )
    file_id = message.document.file_id
    query = await db.files.count_documents({}) / 3 + 1
    #try:
    # Загрузка и чтение PDF
    file = await message.bot.download(file_id)
    await db_create_file(db, message.from_user.id, 0, bson.Binary(file.read()), query)
    text = await read_pdf(file)
    
    # Извлечение данных из состояния пользователя
    user_data = await state.get_data()
    profile = await db_find_user_profile(db, message.from_user.id, user_data['name'])
    if profile['sex']:
        profile['sex'] = 'Мужчина'
    else:
        profile['sex'] = 'Женщина'

    table_text, table_text_deviation = await retrieve_table_from_text(text)
    await db_create_file(db, message.from_user.id, 2, table_text, query)

    # Формирование запроса для GPT-4
    formatter = {'age': profile['age'], 'sex': profile['sex'], 'table_text': table_text, 'table_text_deviation': table_text_deviation, 'diseases': profile['diseases']}
    
    prompt = config.prompt.get_secret_value().format(**formatter)

    analysis = await analyze_table_with_gpt(prompt)
    bioethic_response = await getting_bioethic_response(analysis)
    # Сохранение данных
    analysis_id = await db_create_file(db, message.from_user.id, 3, bioethic_response, query)
    _ = await db_analysis_inc(db, message.from_user.id)
    keyboard = create_file_rating(analysis_id)

    # Отладка: выводим содержимое исходной таблицы
    # await message.reply(
    #     f"Исходная расшифрованная таблица:\n\n<pre><code>{table_text}</code></pre>",
    #     reply_markup=reply.main,
    #     parse_mode="HTML"
    # )

    # Пробуем преобразовать текст в DataFrame
    # try:
    #     df = pd.read_csv(StringIO(table_text))
    #     # await message.reply(f"Столбцы таблицы: {', '.join(df.columns)}", reply_markup=reply.main)
    # except Exception as e:
    #     pass # await message.reply(f"Ошибка при создании DataFrame: {str(e)}", reply_markup=reply.main)

    # Форматирование анализа и отклонений для вывода
    result = re.sub(r'<([^>]*)\n', r'&lt;\1', bioethic_response.replace('&', '&amp'))
    result = re.sub(r'\n([^<]*)>', r'\1&gt;', result)

    # Разделяем текст на предсказания и рекоммендации
    anal, rec = result.split('На основе результатов ваших анализов мы рекомендуем следующие <b>дополнительные исследования:</b>')
    rec = 'На основе результатов ваших анализов мы рекомендуем следующие <b>дополнительные исследования:</b>' + rec

    await message.reply(
        f"{anal}",
        parse_mode="HTML",
        reply_markup=reply.main
    )
    # Вывод результата анализа
    await message.reply(
        f"{rec}",
        parse_mode="HTML",
        reply_markup=keyboard
    )
   #  except Exception as e:
    #    await message.reply(
     #       f"<pre><code>Ошибка: {str(e).replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;')}</code></pre>",
      #      reply_markup=reply.main,
       #     parse_mode="HTML"
        #)


@router.message(Form.user_analyses, F.document.file_name.regexp('.*docx?'))
async def process_docx(message: Message, state: FSMContext):
    from bot import db
    await message.answer(
            'Подождите минуту, Ваши анализы обрабатываются...',
    )
    file_id = message.document.file_id
    query = await db.files.count_documents({}) / 3 + 1
    try:
        file = await message.bot.download(file_id)
        await db_create_file(db, message.from_user.id, 1, bson.Binary(file.read()))
        text = await read_docx(file)
        user_data = await state.get_data()
        profile = await db_find_user_profile(db, message.from_user.id, user_data['name'])
        if profile['sex']:
            profile['sex'] = 'Мужчина'
        else:
            profile['sex'] = 'Женщина'

        table_text, table_text_deviation = await retrieve_table_from_text(text)
        await db_create_file(db, message.from_user.id, 2, table_text, query)

        # Формирование запроса для GPT-4
        formatter = {'age': profile['age'], 'sex': profile['sex'], 'table_text': table_text, 'table_text_deviation': table_text_deviation, 'diseases': profile['diseases']}

        prompt = config.prompt.get_secret_value().format(**formatter)

        analysis = await analyze_table_with_gpt(prompt)
        #тут добавил переменную и после нее в резалт теперь биоэтик респонс
        bioethic_response = await getting_bioethic_response(analysis)

        analysis_id = await db_create_file(db, message.from_user.id, 3, bioethic_response, query)
        _ = await db_analysis_inc(db, message.from_user.id)
        keyboard = create_file_rating(analysis_id)


        result = re.sub(r'<([^>]*)\n', r'&lt;\1', bioethic_response.replace('&', '&amp'))
        result = re.sub(r'\n([^<]*)>', r'\1&gt;', result)
        # Разделяем текст на предсказания и рекоммендации
        anal, rec = result.split('На основе результатов ваших анализов мы рекомендуем следующие <b>дополнительные исследования:</b>')
        rec = 'На основе результатов ваших анализов мы рекомендуем следующие <b>дополнительные исследования:</b>' + rec

        await message.reply(
            f"{anal}",
            parse_mode="HTML",
            reply_markup=reply.main
        )
        # Вывод результата анализа
        await message.reply(
            f"{rec}",
            parse_mode="HTML",
            reply_markup=keyboard
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
