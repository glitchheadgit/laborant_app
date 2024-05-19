import torch

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from utils.states import Docs
from utils.preprocessing import read_docx, read_pdf, format_with_yangex_gpt
from keyboards import reply


router = Router()


@router.message(F.text.in_(["/analysis", "Анализ"]))
async def get_photo(message: Message, state: FSMContext):
    await state.set_state(Docs.user_analyses)
    await message.answer("Пожалуйста, загрузите pdf или docx для анализа", reply_markup=reply.cancel)


@router.message(Docs.user_analyses, F.document.file_name.endswith('.pdf'))
async def process_pdf(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file = await message.bot.download(file_id)
    text = read_pdf(file)
    result = format_with_yangex_gpt(text)
    await message.reply(
        result,
        reply_markup=reply.main,
    )
    await state.clear()


@router.message(Docs.user_analyses, F.document.file_name.regexp('.*docx?'))
async def process_docx(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file = await message.bot.download(file_id)
    text = read_docx(file)
    result = format_with_yangex_gpt(text)
    await message.reply(
        result,
        reply_markup=reply.main,
    )
    await state.clear()


@router.message(CommandStart())
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
