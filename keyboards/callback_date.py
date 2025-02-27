from aiogram.filters.callback_data import CallbackData

'''Определяем формат данных, передаваемых при нажатии на инлайн-кнопки'''


class CelebrityData(CallbackData, prefix='cd'):
    button: str
    name: str
    file_name: str


class QuizData(CallbackData, prefix='QD'):
    button: str
    subject: str | None
