from aiogram.fsm.state import State, StatesGroup


class CreateChildForm(StatesGroup):
    """
    States for creating a new child profile.
    """
    name = State()  # Waiting for child's name and description
    age = State()   # Waiting for child's age
    notes = State() # Waiting for additional notes
