from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    user_analyses = State()
    profile_edit = State()
    profile_delete = State()
    name = State()


class Profile(StatesGroup):
    name = State()
    age = State()
    sex = State()
    user_analyses = State()
    healthy = State()
    diseases = State()