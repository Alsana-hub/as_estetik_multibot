from app.adapters.max.client import MaxClient
from app.adapters.max.keyboards import (
    get_about_menu,
    get_back_main_menu,
    get_contact_menu,
    get_help_choose_menu,
    get_help_result_menu,
    get_main_menu,
    get_service_card_menu,
    get_services_menu,
    get_write_max_menu,
)

from app.core.content import (
    ABOUT_TEXT,
    BEFORE_VISIT_TEXT,
    CERTIFICATES_TEXT,
    CONTACTS_TEXT,
    HELP_CHOOSE_TEXT,
    HELP_OPTIONS,
    HELP_QUESTION_TEXT,
    MAIN_MENU_TEXT,
    PRICES_TEXT,
    QUESTION_TEXT,
    WELCOME_TEXT,
    get_service_text,
)

from app.core.referrals import (
    register_referral_client,
)


async def handle_bot_started(
    client: MaxClient,
    update: dict,
) -> None:
    chat_id = update.get("chat_id")

    if not chat_id:
        return

    referral_registered = False

    payload = (
        update.get("payload")
        or ""
    ).strip()

    user = (
        update.get("user")
        or {}
    )

    if payload.lower().startswith(
        "ref_"
    ):
        ref_code = (
            payload[4:]
            .strip()
            .upper()
        )

        user_id = user.get(
            "user_id"
        )

        if ref_code and user_id:
            referral_registered = (
                register_referral_client(
                    platform="max",
                    platform_user_id=str(
                        user_id
                    ),
                    username=user.get(
                        "username"
                    ),
                    first_name=user.get(
                        "name"
                    ),
                    ref_code=ref_code,
                )
            )

    await client.send_message(
        chat_id=chat_id,
        text=WELCOME_TEXT,
        attachments=get_main_menu(),
    )

    if referral_registered:
        await client.send_message(
            chat_id=chat_id,
            text=(
                "🎁 Промокод рекомендации сохранён.\n\n"
                "На первое посещение для вас действует "
                "скидка 10%."
            ),
        )


async def handle_message_created(
    client: MaxClient,
    update: dict,
) -> None:
    message = update.get(
        "message",
        {},
    )

    body = message.get(
        "body",
        {},
    )

    text = body.get(
        "text",
        "",
    )

    chat_id = message.get(
        "recipient",
        {},
    ).get(
        "chat_id"
    )

    if not chat_id:
        return

    if text == "/start":
        await client.send_message(
            chat_id=chat_id,
            text=WELCOME_TEXT,
            attachments=get_main_menu(),
        )


async def handle_callback(
    client: MaxClient,
    update: dict,
) -> None:
    callback = update.get(
        "callback",
        {},
    )

    callback_id = callback.get(
        "callback_id"
    )

    payload = callback.get(
        "payload"
    )

    if not callback_id:
        return

    print(
        "Нажата кнопка MAX:",
        payload,
    )

    if payload == "services":
        await client.answer_callback(
            callback_id=callback_id,
            text="💆 Выберите услугу:",
            attachments=get_services_menu(),
        )
        return

    if payload and payload.startswith(
        "service_"
    ):
        service_key = payload.removeprefix(
            "service_"
        )

        try:
            text = get_service_text(
                service_key
            )
        except KeyError:
            return

        await client.answer_callback(
            callback_id=callback_id,
            text=text,
            attachments=get_service_card_menu(),
        )
        return

    if payload == "prices":
        await client.answer_callback(
            callback_id=callback_id,
            text=PRICES_TEXT,
            attachments=get_back_main_menu(),
        )
        return

    if payload == "help_choose":
        await client.answer_callback(
            callback_id=callback_id,
            text=HELP_CHOOSE_TEXT,
            attachments=get_help_choose_menu(),
        )
        return

    if payload and payload.startswith(
        "help_"
    ):
        help_key = payload.removeprefix(
            "help_"
        )

        if help_key == "question":
            await client.answer_callback(
                callback_id=callback_id,
                text=HELP_QUESTION_TEXT,
                attachments=get_write_max_menu(),
            )
            return

        option = HELP_OPTIONS.get(
            help_key
        )

        if not option:
            return

        await client.answer_callback(
            callback_id=callback_id,
            text=option["text"],
            attachments=get_help_result_menu(),
        )
        return

    if payload == "certificates":
        await client.answer_callback(
            callback_id=callback_id,
            text=CERTIFICATES_TEXT,
            attachments=get_write_max_menu(),
        )
        return

    if payload == "contacts":
        await client.answer_callback(
            callback_id=callback_id,
            text=CONTACTS_TEXT,
            attachments=get_contact_menu(),
        )
        return

    if payload == "about":
        await client.answer_callback(
            callback_id=callback_id,
            text=ABOUT_TEXT,
            attachments=get_about_menu(),
        )
        return

    if payload == "before_visit":
        await client.answer_callback(
            callback_id=callback_id,
            text=BEFORE_VISIT_TEXT,
            attachments=get_write_max_menu(),
        )
        return

    if payload == "question":
        await client.answer_callback(
            callback_id=callback_id,
            text=QUESTION_TEXT,
            attachments=get_write_max_menu(),
        )
        return

    if payload == "back_main":
        await client.answer_callback(
            callback_id=callback_id,
            text=MAIN_MENU_TEXT,
            attachments=get_main_menu(),
        )


async def handle_max_update(
    client: MaxClient,
    update: dict,
) -> None:
    update_type = update.get(
        "update_type"
    )

    print(
        "Получено MAX событие:",
        update_type,
    )

    if update_type == "bot_started":
        await handle_bot_started(
            client,
            update,
        )
        return

    if update_type == "message_created":
        await handle_message_created(
            client,
            update,
        )
        return

    if update_type == "message_callback":
        await handle_callback(
            client,
            update,
        )