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
        f'🌟 Добрый день, {message.from_user.first_name}!\nЯ готов Вам помочь разобраться с результатами анализов крови.'
    )
    await message.answer("🔒 Чтобы продолжить, <b>нажмите кнопку ниже</b>, если Вы согласны на обработку персональных данных.", reply_markup=inline.start_button, parse_mode="HTML")
  # Отправляем кнопку "Хорошо"

# Обработка нажатия кнопки "Хорошо"
@router.callback_query(F.data == "ok")
async def ask_age(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Form.ok)
    await callback_query.message.answer('Что вас интересует?', reply_markup=reply.main)
    await callback_query.message.edit_text("Отлично! Давайте начнём.")

@router.message(F.text.in_(["/aboutus", "О нас"]))
async def process_aboutus(message: Message, state: FSMContext):
    await message.answer("👩‍🔬 <b>Наша команда</b> включает специалистов ведущих научно-исследовательских институтов России — ФМБА, Роспотребнадзора и Курчатовского института. Мы развиваем этот продукт при поддержке Сеченовского университета, объединяя медицину и передовые технологии.\n\nНаша цель — помочь вам понять результаты анализов крови через понятные и точные рекомендации. Мы сотрудничаем с опытными врачами и постоянно совершенствуем алгоритмы на основе новейших исследований.\n\n🔒 <b>Ваши данные защищены:</b> Мы не храним и не передаем личные данные. Вся информация используется только для анализа.\n\n📚 <b>Мы стремимся к максимальной точности,</b> совершенствуя наш бот и улучшая сервис на основе вашего опыта.\n\n🤝 <b>Поддержка:</b> Свяжитесь с нами по <a href='mailto:laborantapp@gmail.com'>laborantapp@gmail.com</a> или через <a href='https://forms.gle/6PpFbRT8ozykyu7B8'>Google форму</a>. Мы всегда рады помочь!", parse_mode="HTML")
  # Отправляем кнопку "Хорошо"

@router.message(F.text.in_(["/contacts", "Обратная связь"]))
async def process_contacts(message: Message, state: FSMContext):
    await message.answer("📞 <b>Контакты:</b>\n\nДля вопросов и предложений заполните, пожалуйста, <a href='https://forms.gle/6PpFbRT8ozykyu7B8'>Google форму</a>.\n\nДля сотрудничества и партнерства пишите на 📧 <a href='mailto:laborantapp@gmail.com'>laborantapp@gmail.com</a>", parse_mode="HTML")

@router.message(F.text == "Отменить запрос")
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.ok)
    await message.answer("Готов к работе!", reply_markup=reply.main)

@router.message(Form.ok, F.text.in_(['/analysis', 'Расшифровать анализ']))
async def process_analysis(message: Message, state: FSMContext):
    await state.set_state(Form.age)
    await message.answer('Пожалуйста, укажите Ваш возраст.', reply_markup=reply.cancel)

@router.message(F.text.in_(['/analysis', 'Расшифровать анализ']))
async def process_analysis(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, сначала согласитесь с обработкой персональных данных.')

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
    await bot.send_message(chat_id=callback_query.from_user.id, text="Отправьте, пожалуйста, pdf с анализами.")
    await state.set_state(Form.user_analyses)


