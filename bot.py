import asyncio
import os
from aiogram import Bot, Dispatcher
from handlers import all_handlers_router  # Импорт основного роутера с обработчиками команд

# Создаём экземпляр бота, получая токен из переменных окружения
bot = Bot(token=os.getenv("BOT_TOKEN"))

# Инициализируем диспетчер для управления событиями бота
dp = Dispatcher()


# Функция, вызываемая при старте бота
async def on_start():
    print("✅ Bot is started...")


# Функция, вызываемая при завершении работы бота
async def on_shutdown():
    print("❌ Bot is down now...")


# Асинхронная функция для запуска бота
async def start_bot():
    dp.startup.register(on_start)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(all_handlers_router)  # Подключаем роутеры с обработчиками команд

    await dp.start_polling(bot)  # Запускаем бота и начинаем обработку сообщений


# Основная точка входа в программу
if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("❌ Бот остановлен пользователем.")
