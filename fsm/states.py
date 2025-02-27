from aiogram.fsm.state import State, StatesGroup

class ChatGPTStates(StatesGroup):
    """Состояния для взаимодействия с ChatGPT."""
    wait_for_request = State()  # Ожидание ввода запроса от пользователя

class CelebrityDialog(StatesGroup):
    """Состояния для ведения диалога с известной личностью."""
    wait_for_answer = State()  # Ожидание ответа пользователя в диалоге

class QuizGame(StatesGroup):
    """Состояния для квиз-игры."""
    wait_for_answer = State()  # Ожидание ответа на текущий вопрос
    quiz_next_step = State()  # Выбор дальнейшего действия после ответа