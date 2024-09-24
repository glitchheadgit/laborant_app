from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    age = State()
    sex = State()
    user_analyses = State()
    ok = State()
    diseases_yesno = State()
    diseases = State()