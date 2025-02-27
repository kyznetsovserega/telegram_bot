import asyncio
import difflib
import logging
import re
from pathlib import Path

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery

from classes import gemini, chat_gpt
from fsm.states import ChatGPTStates, CelebrityDialog, QuizGame
from keyboards.inline_keyboards import next_step_keyboard
from keyboards.reply_keyboards import kb_random_facts, kb_start, kb_say_goodbye, kb_back
from .command_handlers import com_start, com_menu, start_quiz

# Настройка логирования
logger = logging.getLogger(__name__)

ai_handler = Router()

# Определяем базовые пути с помощью pathlib
BASE_PATH = Path(__file__).resolve().parent
IMG_PATH = BASE_PATH.parent / 'resources' / 'images'
PROMPT_PATH = BASE_PATH.parent / 'resources' / 'prompts'


def get_prompt_path(filename: str) -> Path | None:
    """
    Возвращает путь к файлу промпта и проверяет его существование.

    """
    prompt_file = PROMPT_PATH / filename
    if prompt_file.exists():
        return prompt_file
    logger.error(f"Ошибка: Файл {prompt_file} не найден.")
    return None


async def handle_ai_response(message: Message, request: list[dict], prompt_file: Path,
                             image_name: str, reply_markup, state: FSMContext):
    """
    Функция обработки запроса к AI с обработкой ошибок.

    """
    caption = None  # Переменная для хранения ответа от AI

    try:
        # Попытка отправить запрос к ChatGPT
        caption = await chat_gpt.text_request(request, str(prompt_file))
        logger.info(f"📜 Ответ ChatGPT: {caption}")
    except Exception as e:
        logger.warning(f"ChatGPT недоступен: {e}, переключаемся на Gemini")

        try:
            # Если ChatGPT не ответил, отправляем запрос к Gemini
            caption = await gemini.text_request(request, str(prompt_file))
            logger.info(f"📜 Ответ Gemini: {caption}")
        except Exception as e:
            logger.error(f"Ошибка при запросе к AI: {e}")

    # Если ни один AI не вернул ответ или он пустой
    if not caption or caption.strip() == "":
        logger.error("❌ AI вернул пустой ответ!")

        error_file = IMG_PATH / "dino.gif"  # Путь к анимации с ошибкой
        if error_file.exists():
            await message.answer_animation(
                FSInputFile(error_file),
                caption="Ошибка при обработке запроса. Попробуйте позже."
            )

        # Очищаем состояние FSM и возвращаем пользователя в главное меню
        await state.clear()
        await asyncio.sleep(1)
        await com_menu(message)
        return None  # Возвращаем None, так как ответа нет

    # Формируем путь к изображению, которое будет отправлено вместе с ответом
    photo_file = FSInputFile(IMG_PATH / image_name)

    # Отправляем пользователю изображение с подписью (ответом от AI)
    await message.answer_photo(
        photo=photo_file,
        caption=caption,
        reply_markup=reply_markup
    )

    logger.info(f"✅ AI-ответ отправлен пользователю: {caption}")

    return caption  # Возвращаем текст ответа от AI


@ai_handler.message(F.text.in_({'Хочу еще факт', 'Рандомный факт'}))
@ai_handler.message(Command('random'))
async def ai_random_fact(message: Message, state: FSMContext):
    """
    Обработчик запроса случайного факта.

    """
    # Показываем, что бот "печатает"
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)

    # Получаем путь к файлу с промптом для случайных фактов
    prompt_file = get_prompt_path('random.txt')

    # Если файл не найден, отправляем сообщение об ошибке
    if not prompt_file:
        await message.answer("Ошибка: Файл с промптом не найден.")
        return

    # Формируем запрос к AI
    request_message = [{'role': 'user', 'content': message.text}]

    # Отправляем запрос к AI через функцию handle_ai_response
    await handle_ai_response(message, request_message, prompt_file, 'random.jpg', kb_random_facts(), state)


@ai_handler.message(ChatGPTStates.wait_for_request)
async def ai_gpt_request(message: Message, state: FSMContext):
    """
    Обработчик запроса к ChatGPT.

    """
    # Если пользователь ввел "Назад", очищаем состояние и возвращаем его в главное меню
    if message.text == 'Назад':
        await com_start(message)
        await state.clear()
        return

    # Показываем, что бот "печатает"
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)

    # Получаем путь к файлу с промптом для ChatGPT
    prompt_file = get_prompt_path('gpt.txt')

    # Если файл не найден, отправляем сообщение об ошибке
    if not prompt_file:
        await message.answer("Ошибка: Файл с промптом не найден.")
        return

    # Формируем запрос к AI
    request_message = [{'role': 'user', 'content': message.text}]

    # Отправляем запрос к AI через функцию handle_ai_response
    await handle_ai_response(message, request_message, prompt_file, 'gpt.jpg', kb_back(), state)


@ai_handler.message(CelebrityDialog.wait_for_answer)
async def celebrity_answer(message: Message, state: FSMContext):
    """
    Обработчик диалога с известной личностью.

    """
    # Если пользователь выбрал "Назад", завершаем диалог и возвращаем его в главное меню
    if message.text == 'Назад':
        await message.answer("✅ Диалог завершён. Возвращаюсь в главное меню.", reply_markup=kb_start())
        await state.clear()  # Очищаем состояние FSM
        await asyncio.sleep(1)  # Небольшая задержка перед возвратом в меню
        await com_start(message)  # Вызываем главное меню
        return

    # Показываем, что бот "печатает"
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)

    # Получаем сохраненные данные состояния FSM
    data = await state.get_data()

    # Получаем имя файла с промптом из состояния
    prompt_name = data.get('prompt')

    # Если промпт отсутствует, отправляем сообщение об ошибке и выходим
    if not prompt_name:
        await message.answer("Ошибка: Не найден промпт в данных состояния.")
        return

    # Если пользователь выбрал "Попрощаться", меняем текст на финальную фразу
    user_text = 'Пока, всего тебе хорошего!' if message.text == 'Попрощаться' else message.text

    # Добавляем сообщение пользователя в историю диалога
    data['dialog'].append({'role': 'user', 'content': user_text})

    # Формируем путь к файлу с промптом
    prompt_file = get_prompt_path(f"{prompt_name}.txt")

    # Отправляем запрос AI через функцию handle_ai_response
    await handle_ai_response(message, data['dialog'], prompt_file, f"{prompt_name}.jpg", kb_say_goodbye(), state)

    # Если пользователь выбрал "Попрощаться", очищаем состояние и возвращаем в главное меню
    if message.text == 'Попрощаться':
        await state.clear()
        await asyncio.sleep(1)
        await com_start(message)


@ai_handler.callback_query(F.data.startswith("quiz_"))
async def quiz_get_question(call: CallbackQuery, state: FSMContext):
    """
    Обработчик получения нового вопроса для квиза.
    """
    topic_key = call.data  # Получаем ключ темы из callback-запроса
    logger.info(f"📌 Получен запрос на новый вопрос по теме: {topic_key}")

    # Если пользователь выбрал выход из квиза
    if topic_key == "quiz_exit":
        user_data = await state.get_data()  # Получаем сохраненные данные пользователя
        score = user_data.get("score", 0)
        await state.clear()
        await call.message.answer(f"📌 Вы вышли из квиза.\n🏆 Твой счёт: {score}")
        await asyncio.sleep(1)
        await com_start(call.message)
        return

    # Если пользователь выбрал начать новый квиз
    if topic_key == "quiz_new":
        await state.clear()
        await start_quiz(call.message, state)
        return

    # Если пользователь выбрал "ещё вопрос" (quiz_more), берем последнюю тему из состояния
    user_data = await state.get_data()
    if topic_key == "quiz_more":
        topic_key = user_data.get("topic")  # Получаем последнюю тему из состояния
        if not topic_key:
            await call.message.answer("❌ Ошибка: Не найдена последняя тема квиза.")
            return

    # Если это новая тема (а не "quiz_more"), сбрасываем счет
    if topic_key != "quiz_more":
        await state.update_data(topic=topic_key, score=0)  # Сохраняем новую тему и обнуляем счет

    # Отображаем сообщение о генерации нового вопроса
    try:
        await call.message.edit_text("📝 Генерирую новый вопрос...")
    except Exception:
        pass  # Если сообщение не удалось изменить (например, оно было удалено), игнорируем ошибку

    # Получаем путь к файлу с промптом для генерации вопросов квиза
    prompt_file = get_prompt_path("quiz.txt")
    if not prompt_file:
        await call.message.answer("❌ Ошибка: файл квиза не найден.")
        return

    # Создаем запрос к AI: передаем в него ключ темы
    request = [{"role": "user", "content": topic_key}]

    # Запрашиваем у AI новый вопрос
    question_text = await handle_ai_response(call.message, request, prompt_file, "quiz.jpg", None, state)

    # Если AI не вернул вопрос, выходим из обработчика
    if not question_text:
        return

    # Переключаем состояние FSM на ожидание ответа пользователя
    await state.set_state(QuizGame.wait_for_answer)
    await state.update_data(last_question=question_text.strip())

    logger.info(f"📌 Установлено состояние: {await state.get_state()}")


@ai_handler.message(StateFilter(QuizGame.wait_for_answer))
async def quiz_correct_answer(message: Message, state: FSMContext):
    """
    Обработчик ответа на квиз.

    """

    def normalize_answer(text):

        """
        Приводит строку к стандартному виду: удаляет знаки препинания,
        лишние пробелы и делает текст строчным.

        """

        return re.sub(r"[^\w\s]", "", text).strip().lower() if text else ""

    def is_similar(ans1: str, ans2: str, threshold: float = 0.9) -> bool:
        """
        Проверяет, похожи ли две строки.
        Сравнение основано на коэффициенте схожести SequenceMatcher.

        """
        return difflib.SequenceMatcher(None, ans1, ans2).ratio() >= threshold or ans1 in ans2 or ans2 in ans1

    # Нормализуем ответ пользователя
    user_answer = normalize_answer(message.text) if message.text else None
    # Если ответ пустой, просим пользователя отправить текстовый вариант
    if not user_answer:
        await message.answer("❌ Пожалуйста, отправьте текстовый ответ.")
        return

    # Получаем данные пользователя (последний вопрос и текущий счет)
    user_data = await state.get_data()
    last_question = user_data.get("last_question")
    score = user_data.get("score", 0)

    # Получаем путь к файлу с промптом для генерации правильных ответов
    prompt_file = get_prompt_path("quiz.txt")
    if not prompt_file:
        await message.answer("❌ Ошибка: файл квиза не найден.")
        return

    # Формируем запрос к AI для получения правильного ответа на последний заданный вопрос
    request = [{"role": "user", "content": f"Дай краткий правильный ответ на вопрос: {last_question}"}]

    # Запрашиваем у AI правильный ответ
    correct_answer = await handle_ai_response(message, request, prompt_file, "quiz.jpg", None, state)

    # Если AI не вернул ответ, прерываем обработчик
    if not correct_answer:
        return

    # Проверяем, насколько ответ пользователя похож на правильный ответ
    if is_similar(user_answer, normalize_answer(correct_answer), 0.9):
        score += 1
        response_text = f"✅ Правильно! (+1)\n🏆 Ваш счёт: {score}"
    else:
        if score > 0:
            score -= 1
            response_text = f"❌ Неправильно! (-1)\n🏆 Ваш счёт: {score}"
        else:
            response_text = f"❌ Неправильно! (0)\n🏆 Ваш счёт: {score}"

    # Обновляем счет пользователя в состоянии
    await state.update_data(score=score)

    # Отправляем пользователю результат с новой клавиатурой
    await message.answer(response_text, reply_markup=next_step_keyboard())
