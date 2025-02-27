import os
import aiofiles
from openai import AsyncOpenAI


class ChatGPT:
    """
    Класс для взаимодействия с ProxyAPI, предоставляющим доступ к модели OpenAI GPT.

    Реализован как синглтон, чтобы в проекте использовался только один экземпляр.
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
        """Инициализация клиента API с использованием ProxyAPI."""
        self._api_key = os.getenv('PROXY_API_KEY')  # Получаем API-ключ из переменных окружения
        self._base_url = "https://api.proxyapi.ru/openai/v1"  # Базовый URL для ProxyAPI
        self._client = self._create_client()  # Создаём клиент API

    def _create_client(self):
        """Создаёт асинхронный клиент OpenAI с указанным API-ключом и URL."""
        return AsyncOpenAI(
            api_key=self._api_key,
            base_url=self._base_url,  # Используем ProxyAPI URL
        )

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
        Отправляет запрос к модели GPT и получает ответ.

        """
        prompt_text = await self._read_prompt(prompt)
        modified_prompt = f"Ответ должен быть не длиннее 250 символов. {prompt_text}"  # Добавляем ограничение длины ответа

        # Формируем список сообщений для запроса
        message_list = [{'role': 'system', 'content': modified_prompt}] + messages

        # Отправляем запрос
        completion = await self._client.chat.completions.create(
            messages=message_list,
            model="gpt-3.5-turbo"
        )

        return completion.choices[0].message.content.strip()  # Возвращаем очищенный от лишних пробелов ответ
