from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    points_off = State()
    points_on = State()
