import hmac
import os

from aiohttp import web

from app.adapters.max.client import MaxClient
from app.adapters.max.handler import handle_max_update


MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN")
MAX_WEBHOOK_SECRET = os.getenv("MAX_WEBHOOK_SECRET")


if not MAX_BOT_TOKEN:
    raise ValueError(
        "MAX_BOT_TOKEN не найден в переменных окружения"
    )


max_client = MaxClient(
    MAX_BOT_TOKEN
)


async def max_webhook_handler(
    request: web.Request,
) -> web.Response:
    if not MAX_WEBHOOK_SECRET:
        print(
            "MAX_WEBHOOK_SECRET не настроен"
        )

        return web.Response(
            status=500,
            text="Webhook secret is not configured",
        )

    received_secret = request.headers.get(
        "X-Max-Bot-Api-Secret",
        "",
    )

    if not hmac.compare_digest(
        received_secret,
        MAX_WEBHOOK_SECRET,
    ):
        print(
            "Неверный секрет MAX webhook"
        )

        return web.Response(
            status=401,
            text="Unauthorized",
        )

    try:
        update = await request.json()

        await handle_max_update(
            max_client,
            update,
        )

    except Exception as error:
        print(
            "Ошибка MAX webhook:",
            error,
        )

        return web.Response(
            status=500,
            text="Webhook error",
        )

    return web.Response(
        status=200,
        text="OK",
    )


def register_max_routes(
    app: web.Application,
) -> None:
    app.router.add_post(
        "/max/webhook",
        max_webhook_handler,
    )