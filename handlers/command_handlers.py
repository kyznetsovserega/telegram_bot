import os
from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.reply_keyboards import kb_start, kb_back
from keyboards.inline_keyboards import ikb_celebrity, quiz_topics_keyboard
from fsm.states import ChatGPTStates, CelebrityDialog

# Создаем роутер команд
command_router = Router()


# Функция для безопасного чтения текстового файла
def _read_file(path: str, default_text: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return file.read().strip()
    return default_text


# Функция для отправки изображения с текстом
async def _send_image_with_text(message: Message, image_filename: str, text_filename: str, keyboard=None):
    image_path = os.path.join("resources", "images", image_filename)
    text_path = os.path.join("resources", "messages", text_filename)

    caption_text = _read_file(text_path, "Главное изображение")

    await message.answer_photo(
        photo=FSInputFile(image_path),
        caption=caption_text,
        reply_markup=keyboard,
    )


# Обработчик команды /start и кнопки "Назад" или "Закончить"
@command_router.message(F.text.in_(['Назад', 'Закончить']))
@command_router.message(Command("start"))
async def com_start(message: Message):
    await _send_image_with_text(message, "main.jpg", "main.txt", kb_start()
                                )


# Обработчик команды /menu и кнопки "МЕНЮ"
@command_router.message(F.text == "МЕНЮ")
@command_router.message(Command("menu"))
async def com_menu(message: Message):
    await message.answer(
        text="Список доступных команд:\n"
             "/start - Главное меню\n"
             "/random - Рандомный факт\n"
             "/gpt - Запрос к ChatGPT\n"
             "/quiz - QUIZ!\n"
             "/talk - Диалог с известной личностью",
    )


# Обработчик команды /gpt и кнопки "Запрос к GPT"
@command_router.message(F.text == "Запрос к GPT")
@command_router.message(Command("gpt"))
async def ai_gpt_command(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)

    await _send_image_with_text(message, "gpt.jpg", "gpt.txt", kb_back()
                                )
    await state.set_state(ChatGPTStates.wait_for_request)


# Обработчик команды /talk и кнопки "Диалог с личностью"
@command_router.message(F.text == "Диалог с личностью")
@command_router.message(Command("talk"))
async def select_celebrity_dialog(message: Message, state: FSMContext):
    image_path = os.path.join("resources", "images", "talk.jpg")
    text_path = os.path.join("resources", "messages", "talk.txt")

    # Читаем текст и берем описание до первого пустого абзаца
    caption_text = _read_file(text_path, "Главное изображение").split("\n\n", 1)[0]

    await message.answer_photo(
        photo=FSInputFile(image_path),
        caption=caption_text,
        reply_markup=ikb_celebrity(),
    )
    await state.set_state(CelebrityDialog.wait_for_answer)


# Обработчик команды /quiz и кнопки "QUIZ!"
@command_router.message(F.text == "QUIZ!")
@command_router.message(Command("quiz"))
async def start_quiz(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.UPLOAD_PHOTO)

    await _send_image_with_text(message, "quiz.jpg", "quiz.txt", quiz_topics_keyboard())
    await state.clear()
