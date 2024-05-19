from aiogram import Router, F, Bot, types
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards import reply, inline, fabrics


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"🌟 Привет, {message.from_user.first_name}!", reply_markup=reply.main
    )


@router.message(F.text.in_(["/links", "Ссылки"]))
async def links(message: Message):
    await message.answer("📖 Ссылки", reply_markup=inline.links)
