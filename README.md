# Telegram Bot

Этот Telegram-бот реализован с использованием библиотеки `aiogram 3.x` и предназначен для различных AI-функций,
включая работу с ChatGPT и Gemini, квизы и диалоги с известными личностями.

## Функции бота

- Генерация случайных фактов
- Интерфейс ChatGPT
- Диалог с известными личностями
- Квиз на три темы (Python, математика, биология)

## Установка

1. **Склонируйте репозиторий** или скачайте файлы проекта.
2. **Создайте виртуальное окружение** (рекомендуется):
    ```sh
    python -m venv venv
    source venv/bin/activate  # для macOS/Linux
    venv\Scripts\activate  # для Windows
    ```
3. **Установите зависимости**:
    ```sh
    pip install -r requirements.txt
    ```
4. **Создайте файл `.env`** и добавьте в него ключи

## Запуск бота

```sh
python bot.py
```

## Структура проекта

telegram_bot/  
│── bot.py  
│── .gitignore  
│── README.md   
│── requirements.txt  
│  
├── classes/ # Модули для работы с AI  
│ ├── __init__.py  
│ ├── chat_gpt.py  
│ ├── gemini.py   
│  
├── fsm/ # Логика состояний  
│ ├── __init__.py  
│ ├── states.py   
│  
├── handlers/ # Обработчики команд и событий  
│ ├── __init__.py  
│ ├── ai_handlers.py  
│ ├── callback_handlers.py  
│ ├── command_handlers.py  
│ ├── keyboards_handlers.py   
│  
├── keyboards/ # Inline и reply-клавиатуры  
│ ├── __init__.py  
│ ├── callback_date.py  
│ ├── inline_keyboards.py  
│ ├── reply_keyboards.py   
│  
├── resources/ # Изображения, текстовые файлы и промты  
│ ├── images/
│ ├── messages/
│ ├── prompts/  
│       
├── .idea/ # Файлы конфигурации PyCharm
│   
└── __pycache__/

## Контакты

https://github.com/kyznetsovserega  
