import io

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from config_reader import config
from utils.states import Form
from utils.model import retrieve_table_from_text, analyze_table_with_gpt
from utils.preprocessing import read_docx, read_pdf, save_data
from keyboards import reply


router = Router()


@router.message(F.text.in_(["/analysis", "Расшифровать анализ"]))
async def get_photo(message: Message, state: FSMContext):
    await state.set_state(Form.user_analyses)
    await message.answer("Пожалуйста, загрузите pdf документ с результатами анализов", reply_markup=reply.cancel)


@router.message(Form.user_analyses, F.document.file_name.endswith('.pdf'))
async def process_pdf(message: Message, state: FSMContext):
    await message.answer(
        'Подождите, Ваши анализы в обработке...',
    )
    file_id = message.document.file_id
    try:
        file = await message.bot.download(file_id)
        text = read_pdf(file)
        user_data = await state.get_data()
        table_text, table_text_deviation = retrieve_table_from_text(text)
        formatter = {'age': user_data['age'], 'sex': user_data['sex'], 'table_text': table_text, 'table_text_deviation': table_text_deviation}
        prompt = config.prompt.get_secret_value().format(**formatter)
        analyses = analyze_table_with_gpt(prompt)
        save_data(message.chat_shared.chat_id, user_data['age'], user_data['sex'], table_text, analyses)
        result =  analyses.replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;')
        await message.reply(
            '<pre><code>' + analyses + '</code></pre>',
            reply_markup=reply.main,
        )
        await message.reply(
            result,
            reply_markup=reply.main,
        )
    except Exception as e:
        await message.reply(
            '<pre><code>' + str(e).replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;') + '</code></pre>',
            reply_markup=reply.main
        )


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
        formatter = {'age': user_data['age'], 'sex': user_data['sex'], 'table_text': table_text, 'table_text_deviation': table_text_deviation}
        prompt = config.prompt.get_secret_value().format(**formatter)
        analyses = analyze_table_with_gpt(prompt)
        save_data(message.chat_shared.chat_id, user_data['age'], user_data['sex'], table_text, analyses)
        result =  analyses.replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;')
        await message.reply(
            '<pre><code>' + analyses + '</code></pre>',
            reply_markup=reply.main,
        )
        await message.reply(
            result,
            reply_markup=reply.main,
        )
    except Exception as e:
        await message.reply(
            '<pre><code>' + str(e).replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;') + '</code></pre>',
            reply_markup=reply.main
        )

@router.message(F.text == "Отменить запрос")
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Готов к работе!", reply_markup=reply.main)

@router.message(Form.user_analyses, ~F.document.file_name.regexp(r'.*.pdf|.*.docx?'))
async def wrong_format_handler(message: Message, state: FSMContext):
    if message.text == "Отменить запрос":
        await state.clear()
        await message.answer("Чего желаете?", reply_markup=reply.main)
    else:
        await message.answer("Отправьте <b>документ</b> в формате <b>docx</b> или <b>pdf</b>!")
