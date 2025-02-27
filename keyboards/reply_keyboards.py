from aiogram.utils.keyboard import ReplyKeyboardBuilder


def kb_start():
    """
    Создаёт клавиатуру для главного меню.
    Включает кнопки для различных функций бота.
    """
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Рандомный факт')
    keyboard.button(text='Запрос к GPT')
    keyboard.button(text='Диалог с личностью')
    keyboard.button(text='QUIZ!')
    keyboard.button(text='МЕНЮ')

    keyboard.adjust(2, 2, 1)

    return keyboard.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню...'
    )


def kb_random_facts():
    """
    Создаёт клавиатуру для раздела случайных фактов.
    """
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Хочу еще факт')
    keyboard.button(text='Закончить')

    return keyboard.as_markup(resize_keyboard=True)


def kb_back():
    """
    Создаёт клавиатуру с кнопкой "Назад".
    """
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Назад')

    return keyboard.as_markup(resize_keyboard=True)


def kb_say_goodbye():
    """
    Создаёт клавиатуру с кнопкой "Попрощаться".
    """
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Попрощаться')

    return keyboard.as_markup(resize_keyboard=True)
