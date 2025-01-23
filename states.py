from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    name = State()
    age = State()
    color = State()

