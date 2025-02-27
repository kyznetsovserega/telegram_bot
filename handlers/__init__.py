from aiogram import Router

from .ai_handlers import ai_handler
from .command_handlers import command_router
from .callback_handlers import callback_router
from .keyboards_handlers import keyboard_router

# Создаем главный роутер, который объединяет все обработчики
all_handlers_router = Router()
all_handlers_router.include_routers(
    ai_handler,
    command_router,
    keyboard_router,
    callback_router
)

# Экспортируем главный роутер
__all__ = ['all_handlers_router']
