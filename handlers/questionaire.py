import torch
import io

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from utils.states import Docs
from utils.model import format_analyses, add_state, predict_diagnoses
from utils.preprocessing import read_docx, read_pdf
from keyboards import reply


router = Router()


@router.message(F.text.in_(["/analysis", "Анализ"]))
async def get_photo(message: Message, state: FSMContext):
    await state.set_state(Docs.user_analyses)
    await message.answer("Пожалуйста, загрузите pdf или docx для анализа", reply_markup=reply.cancel)


@router.message(Docs.user_analyses, F.document.file_name.endswith('.pdf'))
async def process_pdf(message: Message, state: FSMContext):
    await message.answer(
        'Подождите минуту, Ваши анализы обрабатываются...',
    )
    file_id = message.document.file_id
    try:
        file = await message.bot.download(file_id)
        text = read_pdf(file)
        with io.BytesIO() as log:	
            analyses = format_analyses(text)
            log.write(analyses.encode('utf-8'))
            state = add_state(analyses)
            log.write(state.encode('utf-8'))
            result =  predict_diagnoses(state)
            result = result.replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;')
            await message.reply_document(
                document=BufferedInputFile(log, filename='log.txt'),
                caption='<pre><code>' + result + '</code></pre>',
                reply_markup=reply.main,
            )
    except Exception as e:
        await message.reply(
            '<pre><code>' + str(e).replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;') + '</code></pre>',
            reply_markup=reply.main
        )


@router.message(Docs.user_analyses, F.document.file_name.regexp('.*docx?'))
async def process_docx(message: Message, state: FSMContext):
    await message.answer(
            'Подождите минуту, Ваши анализы обрабатываются...',
    )
    file_id = message.document.file_id
    try:
        file = await message.bot.download(file_id)
        text = read_docx(file)
        with io.BytesIO() as log:
            analyses = format_analyses(text)
            log.write(analyses.encode('utf-8'))
            state = add_state(analyses)
            log.write(state.encode('utf-8'))
            result =  predict_diagnoses(state)
            result = result.replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;')
            await message.reply_document(
                document=BufferedInputFile(log, filename='log.txt'),
                caption='<pre><code>' + result + '</code></pre>',
                reply_markup=reply.main,
            )
    except Exception as e:
        await message.reply(
            '<pre><code>' + str(e).replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;') + '</code></pre>',
            reply_markup=reply.main
        )


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Чего желаете?", reply_markup=reply.main)

@router.message(F.text == "Отменить запрос")
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Чего желаете?", reply_markup=reply.main)

@router.message(Docs.user_analyses, ~F.document.file_name.regexp(r'.*.pdf|.*.docx?'))
async def wrong_format_handler(message: Message, state: FSMContext):
    if message.text == "Отменить запрос":
        await state.clear()
        await message.answer("Чего желаете?", reply_markup=reply.main)
    else:
        await message.answer("Отправьте <b>документ</b> в формате <b>docx</b> или <b>pdf</b>!")
