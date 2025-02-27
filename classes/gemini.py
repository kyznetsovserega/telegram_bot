import os
import aiofiles
import google.generativeai as genai


class GeminiAI:
    """
    Класс для взаимодействия с моделью Gemini через Google Generative AI.

    Реализован как Singleton, чтобы в проекте использовался только один экземпляр.
    """

    _instance = None  # Хранит единственный экземпляр класса

    def __new__(cls, *args, **kwargs):
        """
        Реализация паттерна Singleton.

        """
        if cls._instance is None:
            instance = super().__new__(cls)
            cls._instance = instance
        return cls._instance

    def __init__(self):
        """Инициализация модели Gemini с использованием API-ключа ."""
        self._ai_token = os.getenv('GEMINI_TOKEN')  # Получаем API-ключ Gemini
        genai.configure(api_key=self._ai_token)  # Настройка API
        self._model = genai.GenerativeModel("gemini-pro")  # Выбор модели

    @staticmethod
    async def _read_prompt(path: str) -> str:
        """
        Асинхронно читает файл с промптом из директории.

        """
        async with aiofiles.open(os.path.join('prompts', path), 'r', encoding='UTF-8') as file:
            prompt = await file.read()
        return prompt

    async def text_request(self, messages: list[dict[str, str]], prompt: str):
        """
        Отправляет запрос к модели Gemini и получает ответ.

        """
        prompt_text = await self._read_prompt(prompt)
        modified_prompt = f"Ответ должен быть не длиннее 250 символов. {prompt_text}"  # Добавляем ограничение длины ответа

        # Подготовка истории диалога для модели
        conversation = [modified_prompt] + [msg["content"] for msg in messages]

        response = self._model.generate_content(conversation)  # Запрос к модели

        if response and response.text:
            return response.text.strip()  # Возвращаем ответ без лишних пробелов

        return "⚠️ Ошибка: пустой ответ от Gemini."  # Сообщение об ошибке, если ответ пуст
