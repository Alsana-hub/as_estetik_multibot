import os
import re

from app.adapters.max.client import MaxClient
from app.adapters.max.keyboards import (
    get_about_menu,
    get_back_main_menu,
    get_contact_menu,
    get_help_choose_menu,
    get_help_result_menu,
    get_main_menu,
    get_manual_referrers_menu,
    get_referral_admin_menu,
    get_referral_bonus_clients_menu,
    get_referral_bonus_confirm_menu,
    get_referral_cancel_menu,
    get_referral_unpaid_clients_menu,
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
    add_manual_referral_client,
    add_referral_partner,
    get_referral_clients,
    get_referral_partner,
    get_referral_partners,
    get_referral_summary,
    mark_bonus_paid,
    mark_first_visit_paid,
    register_referral_client,
)


MAX_ADMIN_ID = os.getenv(
    "MAX_ADMIN_ID",
    "",
)

ADMIN_STATES: dict[str, dict] = {}


def get_chat_id(
    update: dict,
):
    chat_id = update.get(
        "chat_id"
    )

    if chat_id:
        return chat_id

    message = update.get(
        "message",
        {},
    )

    chat_id = (
        message
        .get("recipient", {})
        .get("chat_id")
    )

    if chat_id:
        return chat_id

    callback = update.get(
        "callback",
        {},
    )

    chat_id = callback.get(
        "chat_id"
    )

    if chat_id:
        return chat_id

    return (
        callback
        .get("message", {})
        .get("recipient", {})
        .get("chat_id")
    )


def get_user_id(
    update: dict,
):
    callback = update.get(
        "callback",
        {},
    )

    callback_user = callback.get(
        "user",
        {},
    )

    user_id = (
        callback_user.get("user_id")
        or callback_user.get("id")
        or callback.get("user_id")
    )

    if user_id:
        return str(user_id)

    user = update.get(
        "user",
        {},
    )

    user_id = (
        user.get("user_id")
        or user.get("id")
    )

    if user_id:
        return str(user_id)

    sender = (
        update
        .get("message", {})
        .get("sender", {})
    )

    user_id = (
        sender.get("user_id")
        or sender.get("id")
    )

    if user_id:
        return str(user_id)

    return None


def get_state_key(
    update: dict,
):
    chat_id = get_chat_id(
        update
    )

    if chat_id:
        return str(chat_id)

    return get_user_id(
        update
    )


def is_admin(
    update: dict,
) -> bool:

    user_id = get_user_id(
        update
    )

    return bool(
        MAX_ADMIN_ID
        and user_id
        and str(user_id)
        == str(MAX_ADMIN_ID)
    )


def get_client_by_id(
    client_id: int,
):
    for row in get_referral_clients():
        if row["id"] == client_id:
            return row

    return None


def build_referral_stats_text() -> str:
    rows = get_referral_summary()

    if not rows:
        return (
            "📊 Реферальная статистика\n\n"
            "Реферальных партнёров пока нет."
        )

    lines = [
        "📊 Реферальная статистика"
    ]

    for row in rows:
        lines.append(
            "\n"
            f"👤 Рекомендатель: {row['name']}\n"
            f"🔑 Код: {row['code']}\n"
            f"👥 Приведено клиентов: "
            f"{row['clients_count']}\n"
            f"✅ Оплатили первый визит: "
            f"{row['paid_clients_count']}\n"
            f"💰 Начислено бонусов: "
            f"{row['total_bonus']} ₽\n"
            f"⏳ Осталось выдать: "
            f"{row['bonus_to_pay']} ₽"
        )

    return "\n".join(lines)


def build_referral_clients_text() -> str:
    rows = get_referral_clients()

    if not rows:
        return (
            "👥 Реферальные клиенты\n\n"
            "Клиентов пока нет."
        )

    lines = [
        "👥 Реферальные клиенты"
    ]

    for row in rows[:20]:

        first_name = (
            row["first_name"]
            or "Имя не указано"
        )

        referrer = (
            row["referrer_name"]
            or "Неизвестно"
        )

        if row["platform"] == "manual":
            source = "Добавлен вручную"
        elif row["platform"] == "telegram":
            source = "Telegram"
        elif row["platform"] == "max":
            source = "MAX"
        else:
            source = row["platform"]

        paid = (
            "✅ Оплачен"
            if row["first_visit_paid"]
            else "⏳ Ещё не оплачен"
        )

        if row["bonus_paid"]:
            bonus = "✅ Бонус выдан"
        elif row["first_visit_paid"]:
            bonus = "⏳ Бонус нужно выдать"
        else:
            bonus = "—"

        lines.append(
            "\n"
            f"👤 Клиент: {first_name}\n"
            f"Рекомендатель: {referrer}\n"
            f"Источник: {source}\n"
            f"Первый визит: {paid}\n"
            f"Бонус: {row['bonus_amount']} ₽\n"
            f"Статус бонуса: {bonus}"
        )

    return "\n".join(lines)


async def handle_bot_started(
    client: MaxClient,
    update: dict,
) -> None:

    chat_id = get_chat_id(
        update
    )

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

        user_id = (
            user.get("user_id")
            or user.get("id")
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
                    first_name=(
                        user.get("name")
                        or user.get("first_name")
                    ),
                    ref_code=ref_code,
                )
            )

    await client.send_message(
        chat_id=chat_id,
        text=WELCOME_TEXT,
        attachments=get_main_menu(
            is_admin=is_admin(
                update
            )
        ),
    )

    if referral_registered:
        await client.send_message(
            chat_id=chat_id,
            text=(
                "🎁 Промокод рекомендации сохранён.\n\n"
                "На первое посещение действует "
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

    text = (
        message
        .get("body", {})
        .get("text", "")
        or ""
    ).strip()

    chat_id = get_chat_id(
        update
    )

    if not chat_id:
        return

    if text == "/myid":
        await client.send_message(
            chat_id=chat_id,
            text=(
                "Ваш MAX ID:\n"
                f"{get_user_id(update)}\n\n"
                "Chat ID:\n"
                f"{chat_id}"
            ),
        )
        return

    if text == "/start":
        await client.send_message(
            chat_id=chat_id,
            text=WELCOME_TEXT,
            attachments=get_main_menu(
                is_admin=is_admin(
                    update
                )
            ),
        )
        return

    if not is_admin(
        update
    ):
        return

    state_key = get_state_key(
        update
    )

    state = ADMIN_STATES.get(
        state_key
    )

    if not state:
        return

    action = state.get(
        "action"
    )

    if action == "partner_name":

        ADMIN_STATES[
            state_key
        ] = {
            "action": "partner_code",
            "partner_name": text,
        }

        await client.send_message(
            chat_id=chat_id,
            text=(
                "Теперь придумайте код.\n\n"
                "Например: OLGA10"
            ),
            attachments=get_referral_cancel_menu(),
        )

        return

    if action == "partner_code":

        code = text.upper()

        if not re.fullmatch(
            r"[A-Z0-9_-]{3,30}",
            code,
        ):
            await client.send_message(
                chat_id=chat_id,
                text="❌ Код не подходит.",
                attachments=get_referral_cancel_menu(),
            )
            return

        name = state.get(
            "partner_name"
        )

        add_referral_partner(
            code=code,
            name=name,
        )

        ADMIN_STATES.pop(
            state_key,
            None,
        )

        await client.send_message(
            chat_id=chat_id,
            text=(
                "✅ Рекомендатель добавлен.\n\n"
                f"👤 {name}\n"
                f"🔑 {code}\n\n"
                f"https://as-estetik.ru/?ref={code}"
            ),
            attachments=get_referral_admin_menu(),
        )

        return

    if action == "manual_client_name":

        ref_code = state.get(
            "ref_code"
        )

        partner = get_referral_partner(
            ref_code
        )

        client_id = add_manual_referral_client(
            first_name=text,
            ref_code=ref_code,
        )

        ADMIN_STATES.pop(
            state_key,
            None,
        )

        await client.send_message(
            chat_id=chat_id,
            text=(
                "✅ Клиент добавлен вручную.\n\n"
                f"👤 Клиент: {text}\n"
                f"🤝 Рекомендатель: "
                f"{partner['name'] if partner else ref_code}\n"
                f"Номер записи: #{client_id}\n\n"
                "Теперь его можно отметить "
                "в разделе «✅ Отметить оплату»."
            ),
            attachments=get_referral_admin_menu(),
        )

        return

    if action == "payment_amount":

        normalized = (
            text
            .replace("₽", "")
            .replace(" ", "")
            .replace(",", ".")
        )

        try:
            payment_amount = float(
                normalized
            )
        except ValueError:
            await client.send_message(
                chat_id=chat_id,
                text="Введите сумму числом.",
                attachments=get_referral_cancel_menu(),
            )
            return

        client_id = state.get(
            "client_id"
        )

        ref_code = state.get(
            "ref_code"
        )

        referral_client = get_client_by_id(
            client_id
        )

        partner = get_referral_partner(
            ref_code
        )

        bonus_percent = (
            partner["bonus_percent"]
            if partner
            else 10
        )

        bonus_amount = round(
            payment_amount
            * bonus_percent
            / 100
        )

        mark_first_visit_paid(
            client_id=client_id,
            bonus_amount=bonus_amount,
        )

        ADMIN_STATES.pop(
            state_key,
            None,
        )

        await client.send_message(
            chat_id=chat_id,
            text=(
                "✅ Первый визит оплачен.\n\n"
                f"👤 Клиент: "
                f"{referral_client['first_name']}\n"
                f"💳 Оплата: {payment_amount:g} ₽\n"
                f"🎁 Бонус: {bonus_amount} ₽"
            ),
            attachments=get_referral_admin_menu(),
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

    admin = is_admin(
        update
    )

    state_key = get_state_key(
        update
    )

    if payload == "ref_admin":

        if not admin:
            return

        ADMIN_STATES.pop(
            state_key,
            None,
        )

        await client.answer_callback(
            callback_id=callback_id,
            text="🔐 Управление реферальной системой",
            attachments=get_referral_admin_menu(),
        )

        return

    if payload == "ref_admin_add":

        if not admin:
            return

        ADMIN_STATES[
            state_key
        ] = {
            "action": "partner_name",
        }

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "➕ Добавление рекомендателя\n\n"
                "Введите имя."
            ),
            attachments=get_referral_cancel_menu(),
        )

        return

    # =====================================================
    # РУЧНОЙ КЛИЕНТ
    # =====================================================

    if payload == "ref_admin_manual_client":

        if not admin:
            return

        partners = get_referral_partners()

        if not partners:
            await client.answer_callback(
                callback_id=callback_id,
                text=(
                    "Сначала добавьте рекомендателя."
                ),
                attachments=get_referral_admin_menu(),
            )
            return

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "➕ Добавить клиента вручную\n\n"
                "Кто порекомендовал клиента?"
            ),
            attachments=get_manual_referrers_menu(
                partners
            ),
        )

        return

    if (
        payload
        and payload.startswith(
            "ref_manual_partner:"
        )
    ):

        if not admin:
            return

        ref_code = (
            payload.split(
                ":",
                1,
            )[1]
            .strip()
            .upper()
        )

        partner = get_referral_partner(
            ref_code
        )

        if not partner:
            return

        ADMIN_STATES[
            state_key
        ] = {
            "action": "manual_client_name",
            "ref_code": ref_code,
        }

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "Введите имя клиента.\n\n"
                f"Рекомендатель: {partner['name']}"
            ),
            attachments=get_referral_cancel_menu(),
        )

        return

    if payload == "ref_admin_stats":

        if not admin:
            return

        await client.answer_callback(
            callback_id=callback_id,
            text=build_referral_stats_text(),
            attachments=get_referral_admin_menu(),
        )

        return

    if payload == "ref_admin_clients":

        if not admin:
            return

        await client.answer_callback(
            callback_id=callback_id,
            text=build_referral_clients_text(),
            attachments=get_referral_admin_menu(),
        )

        return

    if payload == "ref_admin_paid":

        if not admin:
            return

        rows = [
            row
            for row in get_referral_clients()
            if not row["first_visit_paid"]
        ]

        if not rows:
            await client.answer_callback(
                callback_id=callback_id,
                text="Нет клиентов, ожидающих оплаты.",
                attachments=get_referral_admin_menu(),
            )
            return

        await client.answer_callback(
            callback_id=callback_id,
            text="✅ Выберите клиента:",
            attachments=get_referral_unpaid_clients_menu(
                rows
            ),
        )

        return

    if (
        payload
        and payload.startswith(
            "ref_paid_client:"
        )
    ):

        if not admin:
            return

        client_id = int(
            payload.split(
                ":",
                1,
            )[1]
        )

        referral_client = get_client_by_id(
            client_id
        )

        ADMIN_STATES[
            state_key
        ] = {
            "action": "payment_amount",
            "client_id": client_id,
            "ref_code": referral_client["ref_code"],
        }

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "💳 Введите сумму оплаты.\n\n"
                f"Клиент: "
                f"{referral_client['first_name']}\n"
                f"Рекомендатель: "
                f"{referral_client['referrer_name']}"
            ),
            attachments=get_referral_cancel_menu(),
        )

        return

    if payload == "ref_admin_bonus":

        if not admin:
            return

        rows = [
            row
            for row in get_referral_clients()
            if (
                row["first_visit_paid"]
                and not row["bonus_paid"]
            )
        ]

        if not rows:
            await client.answer_callback(
                callback_id=callback_id,
                text="Нет бонусов к выплате.",
                attachments=get_referral_admin_menu(),
            )
            return

        await client.answer_callback(
            callback_id=callback_id,
            text="💰 Выберите бонус:",
            attachments=get_referral_bonus_clients_menu(
                rows
            ),
        )

        return

    if (
        payload
        and payload.startswith(
            "ref_bonus_client:"
        )
    ):

        if not admin:
            return

        client_id = int(
            payload.split(
                ":",
                1,
            )[1]
        )

        referral_client = get_client_by_id(
            client_id
        )

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "Подтвердить выдачу бонуса?\n\n"
                f"Клиент: "
                f"{referral_client['first_name']}\n"
                f"Рекомендатель: "
                f"{referral_client['referrer_name']}\n"
                f"Бонус: "
                f"{referral_client['bonus_amount']} ₽"
            ),
            attachments=get_referral_bonus_confirm_menu(
                client_id
            ),
        )

        return

    if (
        payload
        and payload.startswith(
            "ref_bonus_confirm:"
        )
    ):

        if not admin:
            return

        client_id = int(
            payload.split(
                ":",
                1,
            )[1]
        )

        referral_client = get_client_by_id(
            client_id
        )

        mark_bonus_paid(
            client_id
        )

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "✅ Бонус выдан.\n\n"
                f"Сумма: "
                f"{referral_client['bonus_amount']} ₽"
            ),
            attachments=get_referral_admin_menu(),
        )

        return

    if payload == "ref_admin_cancel":

        if not admin:
            return

        ADMIN_STATES.pop(
            state_key,
            None,
        )

        await client.answer_callback(
            callback_id=callback_id,
            text="🔐 Управление реферальной системой",
            attachments=get_referral_admin_menu(),
        )

        return

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

        await client.answer_callback(
            callback_id=callback_id,
            text=get_service_text(
                service_key
            ),
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

        if option:
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

        ADMIN_STATES.pop(
            state_key,
            None,
        )

        await client.answer_callback(
            callback_id=callback_id,
            text=MAIN_MENU_TEXT,
            attachments=get_main_menu(
                is_admin=admin
            ),
        )


async def handle_max_update(
    client: MaxClient,
    update: dict,
) -> None:

    update_type = update.get(
        "update_type"
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