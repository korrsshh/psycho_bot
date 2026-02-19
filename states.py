from aiogram.fsm.state import State, StatesGroup

class TestStates(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()
    broadcast = State()  # Для админской рассылки