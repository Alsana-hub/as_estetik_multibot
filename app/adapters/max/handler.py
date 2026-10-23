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
    get_referral_admin_menu,
    get_referral_bonus_clients_menu,
    get_referral_bonus_confirm_menu,
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
    add_referral_partner,
    get_referral_clients,
    get_referral_partner,
    get_referral_summary,
    mark_bonus_paid,
    mark_first_visit_paid,
    register_referral_client,
)


MAX_ADMIN_ID = os.getenv(
    "MAX_ADMIN_ID",
    "",
)


# Незавершённые действия админа.
# Если приложение перезапустится во время ввода —
# достаточно начать действие заново.
ADMIN_STATES: dict[str, dict] = {}


# =========================================================
# ПОЛУЧЕНИЕ CHAT ID
# =========================================================

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
        .get(
            "recipient",
            {},
        )
        .get(
            "chat_id"
        )
    )

    if chat_id:
        return chat_id

    chat_id = message.get(
        "chat_id"
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

    callback_message = callback.get(
        "message",
        {},
    )

    return (
        callback_message
        .get(
            "recipient",
            {},
        )
        .get(
            "chat_id"
        )
    )


# =========================================================
# ПОЛУЧЕНИЕ USER ID
# =========================================================

def get_user_id(
    update: dict,
):

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

    message = update.get(
        "message",
        {},
    )

    sender = message.get(
        "sender",
        {},
    )

    user_id = (
        sender.get("user_id")
        or sender.get("id")
    )

    if user_id:
        return str(user_id)

    callback = update.get(
        "callback",
        {},
    )

    callback_user = callback.get(
        "user",
        {},
    )

    user_id = (
        callback.get("user_id")
        or callback_user.get("user_id")
        or callback_user.get("id")
    )

    if user_id:
        return str(user_id)

    return None


# =========================================================
# ID ДЛЯ АДМИН-СОСТОЯНИЙ
# =========================================================

def get_state_key(
    update: dict,
) -> str | None:

    chat_id = get_chat_id(
        update
    )

    if chat_id:
        return str(chat_id)

    user_id = get_user_id(
        update
    )

    if user_id:
        return str(user_id)

    return None


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin(
    update: dict,
) -> bool:

    if not MAX_ADMIN_ID:
        return False

    user_id = get_user_id(
        update
    )

    chat_id = get_chat_id(
        update
    )

    return (
        (
            user_id
            and str(user_id)
            == str(MAX_ADMIN_ID)
        )
        or
        (
            chat_id
            and str(chat_id)
            == str(MAX_ADMIN_ID)
        )
    )


# =========================================================
# КЛИЕНТ ПО ID
# =========================================================

def get_client_by_id(
    client_id: int,
):

    for row in get_referral_clients():

        if row["id"] == client_id:
            return row

    return None


# =========================================================
# СТАТИСТИКА
# =========================================================

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

    return "\n".join(
        lines
    )


# =========================================================
# СПИСОК КЛИЕНТОВ
# =========================================================

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

        username = (
            f"@{row['username']}"
            if row["username"]
            else "нет username"
        )

        referrer_name = (
            row["referrer_name"]
            or "Неизвестно"
        )

        if row["first_visit_paid"]:
            paid_status = "✅ Оплачен"
        else:
            paid_status = "⏳ Ещё не оплачен"

        if row["bonus_paid"]:
            bonus_status = "✅ Бонус выдан"
        elif row["first_visit_paid"]:
            bonus_status = "⏳ Бонус нужно выдать"
        else:
            bonus_status = "—"

        lines.append(
            "\n"
            f"👤 Клиент: {first_name}\n"
            f"MAX: {username}\n"
            f"Рекомендатель: {referrer_name}\n"
            f"Код: {row['ref_code']}\n"
            f"Первый визит: {paid_status}\n"
            f"Бонус: {row['bonus_amount']} ₽\n"
            f"Статус бонуса: {bonus_status}"
        )

    if len(rows) > 20:

        lines.append(
            "\nПоказаны последние 20 клиентов."
        )

    return "\n".join(
        lines
    )


# =========================================================
# BOT STARTED
# =========================================================

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
                "На первое посещение для вас "
                "действует скидка 10%."
            ),
        )


# =========================================================
# СООБЩЕНИЯ
# =========================================================

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

    text = (
        body.get(
            "text",
            "",
        )
        or ""
    ).strip()

    chat_id = get_chat_id(
        update
    )

    if not chat_id:
        return

    # -----------------------------------------------------
    # УЗНАТЬ ID MAX
    # -----------------------------------------------------

    if text == "/myid":

        user_id = get_user_id(
            update
        )

        await client.send_message(
            chat_id=chat_id,
            text=(
                "Ваш MAX ID:\n"
                f"{user_id or 'не удалось определить'}\n\n"
                "Chat ID:\n"
                f"{chat_id}"
            ),
        )

        return

    # -----------------------------------------------------
    # START
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # ДАЛЬШЕ — ТОЛЬКО АДМИН
    # -----------------------------------------------------

    if not is_admin(
        update
    ):
        return

    state_key = get_state_key(
        update
    )

    if not state_key:
        return

    state = ADMIN_STATES.get(
        state_key
    )

    if not state:
        return

    action = state.get(
        "action"
    )

    # -----------------------------------------------------
    # ИМЯ НОВОГО РЕКОМЕНДАТЕЛЯ
    # -----------------------------------------------------

    if action == "partner_name":

        name = text.strip()

        if not name:

            await client.send_message(
                chat_id=chat_id,
                text=(
                    "Введите имя рекомендателя."
                ),
            )

            return

        ADMIN_STATES[
            state_key
        ] = {
            "action": "partner_code",
            "partner_name": name,
        }

        await client.send_message(
            chat_id=chat_id,
            text=(
                "Теперь придумайте код.\n\n"
                "Используйте латинские буквы "
                "и цифры.\n\n"
                "Например:\n"
                "OLGA10"
            ),
        )

        return

    # -----------------------------------------------------
    # КОД НОВОГО РЕКОМЕНДАТЕЛЯ
    # -----------------------------------------------------

    if action == "partner_code":

        code = text.upper()

        if not re.fullmatch(
            r"[A-Z0-9_-]{3,30}",
            code,
        ):

            await client.send_message(
                chat_id=chat_id,
                text=(
                    "❌ Код не подходит.\n\n"
                    "Используйте латинские буквы "
                    "и цифры.\n\n"
                    "Например:\n"
                    "OLGA10"
                ),
            )

            return

        name = state.get(
            "partner_name",
            "",
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
                f"👤 Имя: {name}\n"
                f"🔑 Код: {code}\n\n"
                "Персональная ссылка:\n"
                f"https://as-estetik.ru/?ref={code}"
            ),
            attachments=get_referral_admin_menu(),
        )

        return

    # -----------------------------------------------------
    # СУММА ПЕРВОГО ВИЗИТА
    # -----------------------------------------------------

    if action == "payment_amount":

        normalized = (
            text
            .replace("₽", "")
            .replace(" ", "")
            .replace(",", ".")
            .strip()
        )

        try:

            payment_amount = float(
                normalized
            )

        except ValueError:

            await client.send_message(
                chat_id=chat_id,
                text=(
                    "❌ Не поняла сумму.\n\n"
                    "Введите только число.\n\n"
                    "Например:\n"
                    "2700"
                ),
            )

            return

        if payment_amount <= 0:

            await client.send_message(
                chat_id=chat_id,
                text=(
                    "Сумма должна быть "
                    "больше нуля."
                ),
            )

            return

        client_id = state.get(
            "client_id"
        )

        ref_code = state.get(
            "ref_code"
        )

        referral_client = (
            get_client_by_id(
                client_id
            )
        )

        if not referral_client:

            ADMIN_STATES.pop(
                state_key,
                None,
            )

            await client.send_message(
                chat_id=chat_id,
                text=(
                    "Клиент не найден."
                ),
            )

            return

        partner = get_referral_partner(
            ref_code
        )

        bonus_percent = 10

        if partner:

            bonus_percent = (
                partner["bonus_percent"]
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

        client_name = (
            referral_client["first_name"]
            or "Без имени"
        )

        referrer_name = (
            referral_client["referrer_name"]
            or referral_client["ref_code"]
        )

        await client.send_message(
            chat_id=chat_id,
            text=(
                "✅ Первый визит отмечен "
                "как оплаченный.\n\n"
                f"👤 Клиент: {client_name}\n"
                f"🤝 Рекомендатель: "
                f"{referrer_name}\n"
                f"💳 Оплата клиента: "
                f"{payment_amount:g} ₽\n"
                f"🎁 Бонус рекомендателю "
                f"{bonus_percent}%: "
                f"{bonus_amount} ₽\n\n"
                "Бонус теперь находится "
                "в разделе «Осталось выдать»."
            ),
            attachments=get_referral_admin_menu(),
        )

        return


# =========================================================
# CALLBACK
# =========================================================

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

    admin = is_admin(
        update
    )

    state_key = get_state_key(
        update
    )

    # =====================================================
    # РЕФЕРАЛЬНАЯ АДМИНКА
    # =====================================================

    if payload == "ref_admin":

        if not admin:
            return

        if state_key:

            ADMIN_STATES.pop(
                state_key,
                None,
            )

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "🔐 Управление реферальной системой\n\n"
                "Здесь можно добавить рекомендателя, "
                "посмотреть клиентов, отметить оплату "
                "и выдачу бонуса."
            ),
            attachments=get_referral_admin_menu(),
        )

        return

    # -----------------------------------------------------
    # ДОБАВИТЬ ПАРТНЁРА
    # -----------------------------------------------------

    if payload == "ref_admin_add":

        if not admin:
            return

        if not state_key:
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
                "Напишите имя человека, "
                "который будет рекомендовать вас.\n\n"
                "Например:\n"
                "Ольга"
            ),
        )

        return

    # -----------------------------------------------------
    # СТАТИСТИКА
    # -----------------------------------------------------

    if payload == "ref_admin_stats":

        if not admin:
            return

        await client.answer_callback(
            callback_id=callback_id,
            text=build_referral_stats_text(),
            attachments=get_referral_admin_menu(),
        )

        return

    # -----------------------------------------------------
    # КЛИЕНТЫ
    # -----------------------------------------------------

    if payload == "ref_admin_clients":

        if not admin:
            return

        await client.answer_callback(
            callback_id=callback_id,
            text=build_referral_clients_text(),
            attachments=get_referral_admin_menu(),
        )

        return

    # -----------------------------------------------------
    # ОТМЕТИТЬ ОПЛАТУ
    # -----------------------------------------------------

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
                text=(
                    "✅ Нет реферальных клиентов, "
                    "ожидающих первого "
                    "оплаченного визита."
                ),
                attachments=get_referral_admin_menu(),
            )

            return

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "✅ Отметить первый "
                "оплаченный визит\n\n"
                "Выберите клиента, который "
                "уже пришёл к вам и оплатил "
                "свой первый сеанс:"
            ),
            attachments=(
                get_referral_unpaid_clients_menu(
                    rows
                )
            ),
        )

        return

    # -----------------------------------------------------
    # ВЫБРАН КЛИЕНТ ДЛЯ ОПЛАТЫ
    # -----------------------------------------------------

    if (
        payload
        and payload.startswith(
            "ref_paid_client:"
        )
    ):

        if not admin:
            return

        if not state_key:
            return

        try:

            client_id = int(
                payload.split(
                    ":",
                    1,
                )[1]
            )

        except (
            ValueError,
            IndexError,
        ):
            return

        referral_client = (
            get_client_by_id(
                client_id
            )
        )

        if not referral_client:

            await client.answer_callback(
                callback_id=callback_id,
                text="Клиент не найден.",
                attachments=get_referral_admin_menu(),
            )

            return

        if referral_client[
            "first_visit_paid"
        ]:

            await client.answer_callback(
                callback_id=callback_id,
                text=(
                    "Этот первый визит "
                    "уже отмечен как оплаченный."
                ),
                attachments=get_referral_admin_menu(),
            )

            return

        ADMIN_STATES[
            state_key
        ] = {
            "action": "payment_amount",
            "client_id": client_id,
            "ref_code": (
                referral_client["ref_code"]
            ),
        }

        client_name = (
            referral_client["first_name"]
            or "Без имени"
        )

        referrer_name = (
            referral_client["referrer_name"]
            or referral_client["ref_code"]
        )

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "💳 Введите сумму, которую "
                "этот клиент фактически оплатил "
                "за первый визит.\n\n"
                f"Клиент: {client_name}\n"
                f"Рекомендатель: "
                f"{referrer_name}\n\n"
                "Например:\n"
                "2700\n\n"
                "Бонус рекомендателю "
                "бот рассчитает автоматически."
            ),
        )

        return

    # -----------------------------------------------------
    # БОНУС ВЫДАН
    # -----------------------------------------------------

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
                text=(
                    "💰 Сейчас нет бонусов, "
                    "которые нужно выдать."
                ),
                attachments=get_referral_admin_menu(),
            )

            return

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "💰 Отметить выданный бонус\n\n"
                "Выберите клиента, за которого "
                "вы уже выдали бонус "
                "рекомендателю:"
            ),
            attachments=(
                get_referral_bonus_clients_menu(
                    rows
                )
            ),
        )

        return

    # -----------------------------------------------------
    # ВЫБРАН БОНУС
    # -----------------------------------------------------

    if (
        payload
        and payload.startswith(
            "ref_bonus_client:"
        )
    ):

        if not admin:
            return

        try:

            client_id = int(
                payload.split(
                    ":",
                    1,
                )[1]
            )

        except (
            ValueError,
            IndexError,
        ):
            return

        referral_client = (
            get_client_by_id(
                client_id
            )
        )

        if not referral_client:

            await client.answer_callback(
                callback_id=callback_id,
                text="Клиент не найден.",
                attachments=get_referral_admin_menu(),
            )

            return

        if referral_client[
            "bonus_paid"
        ]:

            await client.answer_callback(
                callback_id=callback_id,
                text=(
                    "Этот бонус уже отмечен "
                    "как выданный."
                ),
                attachments=get_referral_admin_menu(),
            )

            return

        client_name = (
            referral_client["first_name"]
            or "Без имени"
        )

        referrer_name = (
            referral_client["referrer_name"]
            or referral_client["ref_code"]
        )

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "💰 Подтвердите выдачу бонуса\n\n"
                f"👤 Клиент: {client_name}\n"
                f"🤝 Рекомендатель: "
                f"{referrer_name}\n"
                f"🎁 Сумма бонуса: "
                f"{referral_client['bonus_amount']} ₽\n\n"
                "Вы действительно уже выдали "
                "этот бонус рекомендателю?"
            ),
            attachments=(
                get_referral_bonus_confirm_menu(
                    client_id
                )
            ),
        )

        return

    # -----------------------------------------------------
    # ПОДТВЕРЖДЕНИЕ БОНУСА
    # -----------------------------------------------------

    if (
        payload
        and payload.startswith(
            "ref_bonus_confirm:"
        )
    ):

        if not admin:
            return

        try:

            client_id = int(
                payload.split(
                    ":",
                    1,
                )[1]
            )

        except (
            ValueError,
            IndexError,
        ):
            return

        referral_client = (
            get_client_by_id(
                client_id
            )
        )

        if not referral_client:

            await client.answer_callback(
                callback_id=callback_id,
                text="Клиент не найден.",
                attachments=get_referral_admin_menu(),
            )

            return

        if referral_client[
            "bonus_paid"
        ]:

            await client.answer_callback(
                callback_id=callback_id,
                text=(
                    "Этот бонус уже был выдан."
                ),
                attachments=get_referral_admin_menu(),
            )

            return

        mark_bonus_paid(
            client_id
        )

        client_name = (
            referral_client["first_name"]
            or "Без имени"
        )

        referrer_name = (
            referral_client["referrer_name"]
            or referral_client["ref_code"]
        )

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "✅ Бонус отмечен как выданный.\n\n"
                f"👤 Клиент: {client_name}\n"
                f"🤝 Рекомендатель: "
                f"{referrer_name}\n"
                f"💰 Выдано: "
                f"{referral_client['bonus_amount']} ₽\n\n"
                "Эта сумма больше не будет "
                "учитываться в разделе "
                "«Осталось выдать»."
            ),
            attachments=get_referral_admin_menu(),
        )

        return

    # -----------------------------------------------------
    # ОТМЕНА
    # -----------------------------------------------------

    if payload == "ref_admin_cancel":

        if not admin:
            return

        if state_key:

            ADMIN_STATES.pop(
                state_key,
                None,
            )

        await client.answer_callback(
            callback_id=callback_id,
            text=(
                "🔐 Управление реферальной системой\n\n"
                "Действие отменено."
            ),
            attachments=get_referral_admin_menu(),
        )

        return

    # =====================================================
    # ОБЫЧНЫЕ КНОПКИ БОТА
    # =====================================================

    if payload == "services":

        await client.answer_callback(
            callback_id=callback_id,
            text="💆 Выберите услугу:",
            attachments=get_services_menu(),
        )

        return

    if (
        payload
        and payload.startswith(
            "service_"
        )
    ):

        service_key = (
            payload.removeprefix(
                "service_"
            )
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

    if (
        payload
        and payload.startswith(
            "help_"
        )
    ):

        help_key = (
            payload.removeprefix(
                "help_"
            )
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

        if state_key:

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

        return


# =========================================================
# ОБЩИЙ ОБРАБОТЧИК MAX
# =========================================================

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