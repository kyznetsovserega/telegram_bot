import os
from collections import namedtuple
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callback_date import CelebrityData


def ikb_celebrity():
    """
    Генерирует инлайн-клавиатуру с доступными знаменитостями.

    Кнопки создаются на основе файлов, содержащихся в директории 'resources/prompts'.
    Если файлы отсутствуют или не содержат корректных данных, клавиатура возвращается пустой.
    """
    Celebrity = namedtuple('Celebrity', ['name', 'file_name'])
    keyboard = InlineKeyboardBuilder()

    prompts_path = os.path.join('resources', 'prompts')

    # Проверяем, существует ли папка с промтами
    if not os.path.exists(prompts_path):
        print(f"❌ Ошибка: директория '{prompts_path}' не найдена!")
        return keyboard.as_markup()

    # Получаем список файлов, начинающихся с 'talk_'
    file_list = [file for file in os.listdir(prompts_path) if file.startswith('talk_')]

    if not file_list:
        print("❌ Ошибка: в папке 'prompts' нет подходящих файлов!")
        return keyboard.as_markup()

    celebrity_list = []

    # Обрабатываем каждый файл с промтом
    for file in file_list:
        file_path = os.path.join(prompts_path, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                lines = txt_file.readlines()

                # Берём первую непустую строку как имя знаменитости
                name = next((line.strip() for line in lines if line.strip()), "")

                if not name:
                    print(f"⚠️ Файл '{file}' пуст или содержит только пробельные строки.")
                    continue

                # Создаём объект знаменитости
                celebrity_list.append(Celebrity(name, file.rsplit('.', 1)[0]))

        except Exception as e:
            print(f"❌ Ошибка при чтении '{file}': {e}")
            continue

    if not celebrity_list:
        print("❌ Ошибка: не удалось загрузить ни одной знаменитости из файлов.")
        return keyboard.as_markup()

    # Добавляем кнопки в клавиатуру
    for celebrity in celebrity_list:
        keyboard.button(
            text=celebrity.name.split(" - ")[1].split(".")[0].split(",")[0],  # Получаем только имя
            callback_data=CelebrityData(
                button="cb",
                name=celebrity.name.split(" - ")[1].split(".")[0].split(",")[0].replace(":", ""),  # Без ":"
                file_name=celebrity.file_name,
            ),
        )

    # Устанавливаем количество кнопок в ряду (по одной в строке)
    keyboard.adjust(*[1] * len(celebrity_list))

    return keyboard.as_markup()


# Клавиатура с темами квиза
def quiz_topics_keyboard():
    """
    Возвращает инлайн-клавиатуру с темами для квиза.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Python", callback_data="quiz_prog")],
        [InlineKeyboardButton(text="🔹 Математика", callback_data="quiz_math")],
        [InlineKeyboardButton(text="🔹 Биология", callback_data="quiz_biology")],
    ])


# Клавиатура с выбором следующего шага в квизе
def next_step_keyboard():
    """
    Возвращает инлайн-клавиатуру с вариантами действий после ответа в квизе.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Следующий вопрос", callback_data="quiz_more")],
        [InlineKeyboardButton(text="🔹 Выбрать новую тему", callback_data="quiz_new")],
        [InlineKeyboardButton(text="🔹 Выйти", callback_data="quiz_exit")],
    ])
