from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.reply_keyboards import kb_back

# Создаем роутер для обработки сообщений с клавиатуры
keyboard_router = Router()

# Словарь с ответами на команды и текстовые сообщения
responses = {
    'chatgpt': ('В будущем здесь будет функционал ChatGPT!', kb_back()),
    'рандомный факт': ('Сейчас выдам рандомный факт!', kb_back()),
    '/chatgpt': ('В будущем здесь будет функционал ChatGPT!', kb_back()),
    '/random': ('Сейчас выдам рандомный факт!', kb_back()),
}


@keyboard_router.message(F.text.lower().in_(responses.keys()))  # Обработка текстовых сообщений
@keyboard_router.message(Command('chatgpt'))  # Обработка команды /chatgpt
@keyboard_router.message(Command('random'))  # Обработка команды /random
async def kb_responses(message: Message):
    """
    Обрабатывает команды и текстовые сообщения, отвечая пользователю.

    """
    text_response, keyboard = responses.get(message.text.lower(), ("Команда обработана!", None))

    await message.answer(
        text=text_response,
        reply_markup=keyboard,  # Отправляем ответ с клавиатурой (если есть)
    )
