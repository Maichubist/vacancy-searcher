from aiogram.dispatcher.filters.state import State, StatesGroup


class GetProfession(StatesGroup):
    waiting_for_profession = State()


class GetCity(StatesGroup):
    waiting_for_city = State()


class GetResponse(StatesGroup):
    waiting_for_response = State()
