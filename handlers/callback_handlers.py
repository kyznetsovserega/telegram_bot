import asyncio
import logging
from pathlib import Path

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from fsm.states import CelebrityDialog
from keyboards.callback_date import CelebrityData
from keyboards.reply_keyboards import kb_back

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

callback_router = Router()

# Пути к ресурсам
BASE_PATH = Path(__file__).resolve().parent.parent  # Корневая директория проекта
IMG_PATH = BASE_PATH / "resources" / "images"  # Папка с изображениями
PROMPT_PATH = BASE_PATH / "resources" / "prompts"  # Папка с промтами


@callback_router.callback_query(CelebrityData.filter())
async def select_celebrity(callback: CallbackQuery, callback_data: CelebrityData, state: FSMContext):
    """Обработчик выбора знаменитости."""
    if callback_data.button != "cb":  # Проверяем кнопку вручную
        return

    await state.set_state(CelebrityDialog.wait_for_answer)
    await state.update_data(
        name=callback_data.name,
        dialog=[],
        prompt=callback_data.file_name,
    )

    photo_path = IMG_PATH / f"{callback_data.file_name}.jpg"

    try:
        # Проверяем существование файла в отдельном потоке
        file_exists = await asyncio.to_thread(photo_path.is_file)

        if not file_exists:
            logger.error(f"Изображение {photo_path} не найдено.")
            await callback.message.answer(f"❌ Ошибка: изображение {photo_path.name} не найдено.")
            return

        photo_file = FSInputFile(str(photo_path))

        await callback.message.answer_photo(
            photo=photo_file,
            caption=f"🤖 Вас приветствует {callback_data.name}!\nЗадайте вопрос первым:",
            reply_markup=kb_back(),
        )

    except Exception as e:
        logger.exception(f"Ошибка при обработке изображения {photo_path}: {e}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.")

    await callback.answer()  # Закрываем callback-запрос
