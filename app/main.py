import os

from aiohttp import web
from dotenv import load_dotenv


# Сначала загружаем переменные окружения
load_dotenv()


# Только после загрузки .env импортируем адаптеры
from app.adapters.max.webhook import register_max_routes
from app.adapters.telegram.bot import start_telegram_polling


async def health_handler(
    request: web.Request,
) -> web.Response:
    return web.Response(
        text="As_estetik multibot is running"
    )


def create_app() -> web.Application:
    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    register_max_routes(
        app
    )

    return app


async def main() -> None:
    app = create_app()

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    port = int(
        os.getenv(
            "PORT",
            "8080",
        )
    )

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port,
    )

    await site.start()

    print(
        f"As_estetik multibot запущен на порту {port}"
    )
    print(
        "MAX: webhook /max/webhook"
    )
    print(
        "Telegram: polling"
    )

    await start_telegram_polling()


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        main()
    )