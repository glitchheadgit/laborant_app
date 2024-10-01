from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from utils.model import diseases_check
from utils.states import Form, Profile
from utils.laborantdb import db_create_user, db_add_user_profile, db_delete_user_profile, db_create_file, db_find_user_profile, db_find_user_profiles, db_check_confirmation, db_rate_file
from keyboards import reply, inline
from config_reader import config
from bot import db

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
@router.callback_query(F.data == "policy_confirmed")
async def ask_age(callback_query: CallbackQuery, state: FSMContext):
    _ = await db_create_user(db, callback_query.from_user.id)
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
    await state.set_state(state=None)
    await message.answer("Готов к работе!", reply_markup=reply.main)

@router.message(F.text.in_(["/profiles", "Профили"]))
async def show_profiles(message: Message, state: FSMContext, bot: Bot):
    check = await db_check_confirmation(db, message.from_user.id)
    if check:
        await state.set_state(Form.profile_edit)
        profiles = await db_find_user_profiles(db, message.from_user.id)
        keyboard = InlineKeyboardBuilder()
        for profile in profiles["profiles"]:
            keyboard.add(InlineKeyboardButton(text=profile["name"], callback_data=profile["name"]))
        if len(profiles["profiles"]) < 2:
            keyboard.add(InlineKeyboardButton(text="Добавить профиль", callback_data="create"))
        keyboard.add(InlineKeyboardButton(text="Удалить профиль", callback_data="delete"))
        keyboard.adjust(2, 1)
        await bot.send_message(text='Выберите профиль.', chat_id=message.from_user.id, parse_mode="HTML", reply_markup=keyboard.as_markup())
    else:
        await bot.send_message(text='Пожалуйста, сначала согласитесь с обработкой персональных данных.', chat_id=message.from_user.id, parse_mode="HTML")


@router.callback_query(Form.profile_edit, F.data == "delete")
async def delete_profile_choice(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Form.profile_delete)
    profiles = await db_find_user_profiles(db, callback_query.from_user.id)
    keyboard = InlineKeyboardBuilder()
    for profile in profiles["profiles"]:
        keyboard.add(InlineKeyboardButton(text=profile["name"], callback_data=profile["name"]))
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(text='Выберите профиль для удаления.', chat_id=callback_query.from_user.id, parse_mode="HTML", reply_markup=keyboard.as_markup())


@router.callback_query(Form.profile_delete)
async def delete_profile(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await db_delete_user_profile(db, callback_query.from_user.id, callback_query.data)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

    await bot.send_message(text=f'Профиль "{callback_query.data}" был успешно удален.', chat_id=callback_query.from_user.id, parse_mode="HTML", reply_markup=reply.main)


@router.callback_query(Form.profile_edit, F.data == "create")
async def create_profile(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Profile.name)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(text='Пожалуйста, укажите имя профиля.', chat_id=callback_query.from_user.id, reply_markup=reply.cancel)


@router.callback_query(Form.profile_edit, ~F.data.in_(["create", "delete"]))
async def set_profile(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    profile = await db_find_user_profile(db, callback_query.from_user.id, callback_query.data)

    await state.set_state(Form.user_analyses)
    await state.update_data(name=profile['name'])
    sex = 'Мужчина' if profile['sex'] else 'Женщина'
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

    if profile['healthy']:
        await bot.send_message(text=f'Готов к работе!\n\nВыбран профиль "{profile['name']}"\n<b>Возраст</b>: {profile["age"]}\n<b>Пол</b>: {sex}\n <b>Наличие заболеваний</b>: отсутствуют', chat_id=callback_query.from_user.id, reply_markup=reply.main)
    else:
        await bot.send_message(text=f'Готов к работе!\n\nВыбран профиль "{profile['name']}"\n<b>Возраст</b>: {profile["age"]}\n<b>Пол</b>: {sex}\n <b>Указанные болезни</b>: {profile["diseases"]}', chat_id=callback_query.from_user.id, reply_markup=reply.main)


@router.message(Profile.name)
async def set_profile_name(message: Message, state: FSMContext, bot: Bot):
    if not await db_find_user_profile(db, message.from_user.id, message.text) is None:
        await bot.send_message(text='Профиль с этим именем уже существует.', chat_id=message.from_user.id, reply_markup=reply.cancel)
    else:
        await state.update_data(name=message.text)
        await state.set_state(Profile.age)
        await bot.delete_message(message.chat.id,message.message_id - 1)
        await bot.send_message(text='Пожалуйста, укажите Ваш возраст.', chat_id=message.from_user.id, reply_markup=reply.cancel)


@router.message(Form.user_analyses, F.text.in_(['/analysis', 'Расшифровать анализ']))
async def process_analysis(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, отправьте pdf/docx для анализа.', reply_markup=reply.cancel)


@router.message(F.text.in_(['/analysis', 'Расшифровать анализ']))
async def process_analysis(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, сначала выберите профиль.')


@router.message(Profile.age, F.text.regexp(r'.*\D'))
async def age_answer_bad(message: Message, state: FSMContext):
    await message.answer(f'Пожалуйста, укажите возраст с помощью цифр (целочисленно).')


@router.message(Profile.age, F.text.regexp(r'^\d+$'))
async def age_answer_good(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(age=int(message.text)) 
    await bot.delete_message(message.chat.id,message.message_id - 1)
    await message.answer('Теперь укажите, пожалуйста, пол:', reply_markup=inline.sex)
    await state.set_state(Profile.sex)


@router.message(Profile.sex)
async def sex_answer_bad(message: Message, state: FSMContext):
    await message.answer('Для выбора, пожалуйста, воспользуйтесь кнопками.')


@router.callback_query(Profile.sex)
async def sex_answer_good(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(sex=callback_query.data == "мужской")
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text="Есть ли у Вас какие-либо <b>хронические</b> или <b>наследственные заболевания</b>?", reply_markup=inline.diseases, parse_mode="HTML")
    await state.set_state(Profile.healthy)


@router.message(Profile.healthy)
async def disease_answer_bad(message: Message, state: FSMContext):
    await message.answer('Для выбора, пожалуйста, воспользуйтесь кнопками.')


@router.callback_query(Profile.healthy)
async def disease_answer_good(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    if callback_query.data == "T":
        await state.update_data(healthy=callback_query.data == "T")
        profile = await state.get_data()
        profile["diseases"] = None
        _ = await db_add_user_profile(db, callback_query.from_user.id, **profile)
        sex = 'Мужчина' if profile['sex'] else 'Женщина'
        await state.set_state(Form.user_analyses)
        await state.update_data(name=profile['name'])
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(text=f'Готов к работе!\n\nВыбран профиль "{profile['name']}"\n<b>Возраст</b>: {profile["age"]}\n<b>Пол</b>: {sex}\n<b>Наличие заболеваний</b>: отсутствуют', chat_id=callback_query.from_user.id, parse_mode="HTML", reply_markup=reply.main)
    else:
        await state.set_state(Profile.diseases)
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=callback_query.from_user.id, text="Пожалуйста, напишите, какие у Вас есть <b>хронические</b> либо <b>наследственные заболевания</b>.", parse_mode="HTML")
        

#@router.message(Form.diseases)
#async def sex_answer_bad(message: Message, state: FSMContext, bot: Bot):
 #   await state.update_data(diseases=message.text)
  #  profile = await state.get_data()
   # await message.answer(f'Готов к работе! Вы указали,\nВозраст: {profile["age"]}\nПол: {profile["sex"]}\nНаличие заболеваний: {profile['diseases']}')
    #await bot.send_message(chat_id=message.from_user.id, text="Отправьте, пожалуйста, pdf с анализами.")
    #await state.set_state(Form.user_analyses)

    # await bot.send_message(chat_id=callback_query.from_user.id, text="Отправьте, пожалуйста, pdf с анализами.")
    # await state.set_state(Form.user_analyses)


#Предложение чатагпт
@router.message(Profile.diseases)
async def set_diseases(message: Message, state: FSMContext, bot: Bot):

    # Прогоняем через функцию фильтрации diseases_check
    diseases_filtered = diseases_check(message.text)  # Предполагаем, что эта функция уже написана
    # Обновляем данные в состоянии FSM, сохраняем отфильтрованные данные
    await state.update_data(diseases=diseases_filtered)
    await bot.delete_message(message.chat.id,message.message_id - 1)

    # Получаем остальные данные пользователя из состояния
    profile = await state.get_data()
    profile['healthy'] = False
    _ = await db_add_user_profile(db, message.from_user.id, **profile)
    await state.set_state(Form.user_analyses)
    await state.update_data(name=profile['name'])
    # Отправляем сообщение пользователю с подтверждением введенной информации
    sex = 'Мужчина' if profile['sex'] else 'Женщина'
    await bot.send_message(
        text=f'Готов к работе!\n\nВыбран профиль "{profile['name']}"\n<b>Возраст</b>: {profile["age"]}\n<b>Пол</b>: {sex}\n<b>Указанные болезни</b>: {profile["diseases"]}',
        chat_id=message.from_user.id,
        parse_mode="HTML",
        reply_markup=reply.main
    )


@router.callback_query(F.data.startswith('rating_'))
async def disease_answer_good(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    _, analysis_id, rating = callback_query.data.split('_')
    await db_rate_file(db, callback_query.from_user.id, analysis_id, int(rating))
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id, 
        reply_markup=None
    )