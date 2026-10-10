import os

from aiogram import Bot, Dispatcher

from app.adapters.telegram.handler import router


TELEGRAM_BOT_TOKEN = (
    os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("BOT_TOKEN")
)


if not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN или BOT_TOKEN "
        "не найден в переменных окружения"
    )


telegram_bot = Bot(
    token=TELEGRAM_BOT_TOKEN
)

telegram_dispatcher = Dispatcher()

telegram_dispatcher.include_router(
    router
)


async def start_telegram_polling() -> None:
    print(
        "Telegram бот запущен в режиме polling"
    )

    await telegram_dispatcher.start_polling(
        telegram_bot
    )