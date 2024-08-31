from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    age = State()
    sex = State()
    user_analyses = State()