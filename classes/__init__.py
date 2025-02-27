from .gemini import GeminiAI
from .chat_gpt import ChatGPT

# Создание единственных экземпляров AI-моделей
chat_gpt = ChatGPT()
gemini = GeminiAI()

__all__ = [
    'chat_gpt',
    'gemini'
]
