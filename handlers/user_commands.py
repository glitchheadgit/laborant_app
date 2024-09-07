from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from utils.states import Form
from keyboards import reply, inline


router = Router()

@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        f'🌟 Добрый день, {message.from_user.first_name}!\nПрежде чем начнем, пожалуйста, укажите возраст и пол человека, чьи анализы мы будем анализировать.\n\nЭто важно!'
    )
    await message.answer("🔒 Чтобы продолжить, <b>нажмите кнопку ниже</b>, если Вы прочитали сообщение выше и согласны на обработку персональных данных.", reply_markup=inline.start_button, parse_mode="HTML")
  # Отправляем кнопку "Хорошо"

# Обработка нажатия кнопки "Хорошо"
@router.callback_query(F.data == "ok")
async def ask_age(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Отлично!\nУкажите, пожалуйста, возраст.")
    await state.set_state(Form.age)


@router.message(Form.age, F.text.regexp(r'.*\D'))
async def age_answer_bad(message: Message, state: FSMContext):
    await message.answer(f'Пожалуйста, укажите возраст с помощью цифр (целочисленно).')


@router.message(Form.age, F.text.regexp(r'^\d+$'))
async def age_answer_good(message: Message, state: FSMContext):
    await state.update_data(age=message.text)    
    await message.answer('Спасибо!\nТеперь укажите, пожалуйста, пол:', reply_markup=inline.sex)
    await state.set_state(Form.sex)


@router.message(Form.sex)
async def sex_answer_bad(message: Message, state: FSMContext):
    await message.answer('Для выбора, пожалуйста, воспользуйтесь кнопками.')


@router.callback_query(Form.sex)
async def sex_answer_good(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(sex=callback_query.data)
    user_data = await state.get_data()
    await callback_query.answer(f'Готов к работе! Вы указали,\nВозраст: {user_data["age"]}\nПол: {user_data["sex"]}')
    await bot.send_message(chat_id=callback_query.from_user.id, text="Чего желаете?", reply_markup=reply.main)
    await state.set_state(Form.user_analyses)


