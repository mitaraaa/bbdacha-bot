from aiogram.fsm.state import State, StatesGroup


class CreateTournament(StatesGroup):
    name = State()
    year = State()
    table_url = State()
    confirm = State()


class UpdateTournament(StatesGroup):
    waiting_for_name = State()
    waiting_for_year = State()
    waiting_for_url = State()
    waiting_for_delete = State()
