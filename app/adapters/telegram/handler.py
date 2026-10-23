import os
import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.adapters.telegram.keyboards import (
    get_booking_menu,
    get_contacts_menu,
    get_group_menu,
    get_help_menu,
    get_main_menu,
    get_question_menu,
    get_referral_admin_menu,
    get_services_menu,
)

from app.core.content import (
    ABOUT_TEXT,
    BEFORE_VISIT_TEXT,
    CERTIFICATES_TEXT,
    CONTACTS_TEXT,
    HELP_CHOOSE_TEXT,
    HELP_OPTIONS,
    HELP_QUESTION_TEXT,
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


router = Router()

TELEGRAM_ADMIN_ID = os.getenv(
    "TELEGRAM_ADMIN_ID"
)


# =========================================================
# СОСТОЯНИЯ АДМИН-ПАНЕЛИ
# =========================================================

class ReferralAdminStates(StatesGroup):
    waiting_partner_name = State()
    waiting_partner_code = State()
    waiting_payment_amount = State()


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin_user(
    user_id: int | None,
) -> bool:

    if not user_id:
        return False

    if not TELEGRAM_ADMIN_ID:
        return False

    return (
        str(user_id)
        == str(TELEGRAM_ADMIN_ID)
    )


def is_admin_message(
    message: Message,
) -> bool:

    if not message.from_user:
        return False

    return is_admin_user(
        message.from_user.id
    )


def is_admin_callback(
    callback: CallbackQuery,
) -> bool:

    if not callback.from_user:
        return False

    return is_admin_user(
        callback.from_user.id
    )


# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================================================

def get_client_by_id(
    client_id: int,
):
    rows = get_referral_clients()

    for row in rows:

        if row["id"] == client_id:
            return row

    return None


def get_client_title(
    row,
) -> str:

    first_name = (
        row["first_name"]
        or "Без имени"
    )

    referrer = (
        row["referrer_name"]
        or row["ref_code"]
        or "—"
    )

    return (
        f"Клиент: {first_name} | "
        f"Рекомендатель: {referrer}"
    )


def get_unpaid_clients_menu() -> InlineKeyboardMarkup:

    rows = get_referral_clients()

    buttons = []

    for row in rows:

        if row["first_visit_paid"]:
            continue

        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_client_title(row),
                    callback_data=(
                        f"ref_paid_client:"
                        f"{row['id']}"
                    ),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="↩️ Отмена",
                callback_data="ref_admin_cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def get_bonus_clients_menu() -> InlineKeyboardMarkup:

    rows = get_referral_clients()

    buttons = []

    for row in rows:

        if not row["first_visit_paid"]:
            continue

        if row["bonus_paid"]:
            continue

        buttons.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"{get_client_title(row)} "
                        f"| Бонус: "
                        f"{row['bonus_amount']} ₽"
                    ),
                    callback_data=(
                        f"ref_bonus_client:"
                        f"{row['id']}"
                    ),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="↩️ Отмена",
                callback_data="ref_admin_cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# =========================================================
# ТЕКСТ СТАТИСТИКИ
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

    return "\n".join(lines)


# =========================================================
# ТЕКСТ СПИСКА КЛИЕНТОВ
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
            f"Telegram: {username}\n"
            f"Рекомендатель: {referrer_name}\n"
            f"Код: {row['ref_code']}\n"
            f"Платформа: {row['platform']}\n"
            f"Первый визит: {paid_status}\n"
            f"Бонус: {row['bonus_amount']} ₽\n"
            f"Статус бонуса: {bonus_status}"
        )

    if len(rows) > 20:

        lines.append(
            "\nПоказаны последние 20 клиентов."
        )

    return "\n".join(lines)


# =========================================================
# MY ID
# =========================================================

@router.message(
    Command("myid")
)
async def show_my_id(
    message: Message,
) -> None:

    if not message.from_user:
        return

    await message.answer(
        f"Ваш Telegram ID:\n"
        f"{message.from_user.id}"
    )


# =========================================================
# ТЕХНИЧЕСКАЯ КОМАНДА ДОБАВЛЕНИЯ ПАРТНЁРА
# =========================================================

@router.message(
    Command("ref_add")
)
async def ref_add(
    message: Message,
    command: CommandObject,
) -> None:

    if not is_admin_message(message):
        return

    if not command.args:

        await message.answer(
            "Использование:\n"
            "/ref_add КОД Имя\n\n"
            "Например:\n"
            "/ref_add OLGA10 Ольга"
        )

        return

    parts = (
        command.args
        .strip()
        .split(
            maxsplit=1
        )
    )

    if len(parts) < 2:

        await message.answer(
            "Нужно указать код и имя."
        )

        return

    code = (
        parts[0]
        .strip()
        .upper()
    )

    name = (
        parts[1]
        .strip()
    )

    add_referral_partner(
        code=code,
        name=name,
    )

    await message.answer(
        "✅ Реферальный партнёр добавлен.\n\n"
        f"👤 {name}\n"
        f"🔑 Код: {code}\n\n"
        "Ссылка:\n"
        f"https://as-estetik.ru/?ref={code}"
    )


# =========================================================
# ТЕХНИЧЕСКИЕ КОМАНДЫ
# =========================================================

@router.message(
    Command("ref_stats")
)
async def ref_stats(
    message: Message,
) -> None:

    if not is_admin_message(message):
        return

    await message.answer(
        build_referral_stats_text()
    )


@router.message(
    Command("ref_clients")
)
async def ref_clients(
    message: Message,
) -> None:

    if not is_admin_message(message):
        return

    await message.answer(
        build_referral_clients_text()
    )


# =========================================================
# ГЛАВНАЯ АДМИН-ПАНЕЛЬ
# =========================================================

@router.message(
    F.text == "🔐 Рефералы"
)
async def show_referral_admin(
    message: Message,
    state: FSMContext,
) -> None:

    if not is_admin_message(message):
        return

    await state.clear()

    await message.answer(
        "🔐 Управление реферальной системой\n\n"
        "Здесь можно добавить рекомендателя, "
        "посмотреть клиентов, отметить оплату "
        "и выдачу бонуса.",
        reply_markup=get_referral_admin_menu(),
    )


# =========================================================
# СТАТИСТИКА
# =========================================================

@router.callback_query(
    F.data == "ref_admin_stats"
)
async def referral_admin_stats(
    callback: CallbackQuery,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    if callback.message:

        await callback.message.answer(
            build_referral_stats_text()
        )

    await callback.answer()


# =========================================================
# КЛИЕНТЫ
# =========================================================

@router.callback_query(
    F.data == "ref_admin_clients"
)
async def referral_admin_clients(
    callback: CallbackQuery,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    if callback.message:

        await callback.message.answer(
            build_referral_clients_text()
        )

    await callback.answer()


# =========================================================
# ДОБАВИТЬ ПАРТНЁРА
# =========================================================

@router.callback_query(
    F.data == "ref_admin_add"
)
async def referral_admin_add(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    await state.clear()

    await state.set_state(
        ReferralAdminStates.waiting_partner_name
    )

    if callback.message:

        await callback.message.answer(
            "➕ Добавление рекомендателя\n\n"
            "Напишите имя человека, "
            "который будет рекомендовать вас.\n\n"
            "Например:\n"
            "Ольга"
        )

    await callback.answer()


@router.message(
    ReferralAdminStates.waiting_partner_name
)
async def referral_partner_name(
    message: Message,
    state: FSMContext,
) -> None:

    if not is_admin_message(message):
        return

    name = (
        message.text
        or ""
    ).strip()

    if not name:

        await message.answer(
            "Введите имя рекомендателя."
        )

        return

    await state.update_data(
        partner_name=name
    )

    await state.set_state(
        ReferralAdminStates.waiting_partner_code
    )

    await message.answer(
        "Теперь придумайте код для этого человека.\n\n"
        "Используйте латинские буквы "
        "и цифры.\n\n"
        "Например:\n"
        "OLGA10"
    )


@router.message(
    ReferralAdminStates.waiting_partner_code
)
async def referral_partner_code(
    message: Message,
    state: FSMContext,
) -> None:

    if not is_admin_message(message):
        return

    code = (
        message.text
        or ""
    ).strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9_-]{3,30}",
        code,
    ):

        await message.answer(
            "❌ Код не подходит.\n\n"
            "Используйте только латинские буквы, "
            "цифры, дефис или нижнее подчёркивание.\n\n"
            "Например:\n"
            "OLGA10"
        )

        return

    data = (
        await state.get_data()
    )

    name = data.get(
        "partner_name",
        "",
    )

    add_referral_partner(
        code=code,
        name=name,
    )

    await state.clear()

    await message.answer(
        "✅ Рекомендатель добавлен.\n\n"
        f"👤 Имя: {name}\n"
        f"🔑 Код: {code}\n\n"
        "Его персональная ссылка:\n"
        f"https://as-estetik.ru/?ref={code}\n\n"
        "Эту ссылку можно отправить "
        "рекомендателю.",
        reply_markup=get_referral_admin_menu(),
    )


# =========================================================
# ОТМЕТИТЬ ОПЛАТУ
# =========================================================

@router.callback_query(
    F.data == "ref_admin_paid"
)
async def referral_admin_paid(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    await state.clear()

    rows = [
        row
        for row in get_referral_clients()
        if not row["first_visit_paid"]
    ]

    if not rows:

        await callback.answer(
            "Нет реферальных клиентов, "
            "ожидающих первого оплаченного визита.",
            show_alert=True,
        )

        return

    if callback.message:

        await callback.message.answer(
            "✅ Отметить первый оплаченный визит\n\n"
            "Выберите клиента, который "
            "уже пришёл к вам и оплатил "
            "свой первый сеанс:",
            reply_markup=get_unpaid_clients_menu(),
        )

    await callback.answer()


# =========================================================
# ВЫБОР КЛИЕНТА ДЛЯ ОПЛАТЫ
# =========================================================

@router.callback_query(
    F.data.startswith(
        "ref_paid_client:"
    )
)
async def referral_paid_client_selected(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    if not callback.data:
        return

    try:

        client_id = int(
            callback.data.split(
                ":",
                1,
            )[1]
        )

    except (
        ValueError,
        IndexError,
    ):

        await callback.answer()

        return

    client = get_client_by_id(
        client_id
    )

    if not client:

        await callback.answer(
            "Клиент не найден.",
            show_alert=True,
        )

        return

    if client["first_visit_paid"]:

        await callback.answer(
            "Этот первый визит "
            "уже отмечен как оплаченный.",
            show_alert=True,
        )

        return

    await state.update_data(
        payment_client_id=client_id,
        payment_ref_code=client["ref_code"],
    )

    await state.set_state(
        ReferralAdminStates.waiting_payment_amount
    )

    if callback.message:

        await callback.message.answer(
            "💳 Введите сумму, которую "
            "этот клиент фактически оплатил "
            "за первый визит.\n\n"
            f"Клиент: "
            f"{client['first_name'] or 'Без имени'}\n"
            f"Рекомендатель: "
            f"{client['referrer_name'] or client['ref_code']}\n\n"
            "Например:\n"
            "2700\n\n"
            "Бонус рекомендателю "
            "бот рассчитает автоматически."
        )

    await callback.answer()


# =========================================================
# ВВОД СУММЫ ОПЛАТЫ
# =========================================================

@router.message(
    ReferralAdminStates.waiting_payment_amount
)
async def referral_payment_amount(
    message: Message,
    state: FSMContext,
) -> None:

    if not is_admin_message(message):
        return

    raw_amount = (
        message.text
        or ""
    )

    normalized = (
        raw_amount
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

        await message.answer(
            "❌ Не поняла сумму.\n\n"
            "Введите только число.\n\n"
            "Например:\n"
            "2700"
        )

        return

    if payment_amount <= 0:

        await message.answer(
            "Сумма должна быть больше нуля."
        )

        return

    data = (
        await state.get_data()
    )

    client_id = data.get(
        "payment_client_id"
    )

    ref_code = data.get(
        "payment_ref_code"
    )

    if not client_id or not ref_code:

        await state.clear()

        await message.answer(
            "Не удалось определить клиента.\n"
            "Откройте раздел «🔐 Рефералы» "
            "и попробуйте ещё раз."
        )

        return

    client = get_client_by_id(
        client_id
    )

    if not client:

        await state.clear()

        await message.answer(
            "Клиент больше не найден."
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

    await state.clear()

    client_name = (
        client["first_name"]
        or "Без имени"
    )

    referrer_name = (
        client["referrer_name"]
        or client["ref_code"]
    )

    await message.answer(
        "✅ Первый визит отмечен "
        "как оплаченный.\n\n"
        f"👤 Клиент: {client_name}\n"
        f"🤝 Рекомендатель: {referrer_name}\n"
        f"💳 Оплата клиента: "
        f"{payment_amount:g} ₽\n"
        f"🎁 Бонус рекомендателю "
        f"{bonus_percent}%: "
        f"{bonus_amount} ₽\n\n"
        "Теперь этот бонус будет "
        "отображаться как «К выплате».",
        reply_markup=get_referral_admin_menu(),
    )


# =========================================================
# БОНУС ВЫДАН
# =========================================================

@router.callback_query(
    F.data == "ref_admin_bonus"
)
async def referral_admin_bonus(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    await state.clear()

    rows = [
        row
        for row in get_referral_clients()
        if (
            row["first_visit_paid"]
            and not row["bonus_paid"]
        )
    ]

    if not rows:

        await callback.answer(
            "Сейчас нет бонусов, "
            "которые нужно выдать.",
            show_alert=True,
        )

        return

    if callback.message:

        await callback.message.answer(
            "💰 Отметить выданный бонус\n\n"
            "Выберите клиента, за которого "
            "вы уже выдали бонус рекомендателю:",
            reply_markup=get_bonus_clients_menu(),
        )

    await callback.answer()


# =========================================================
# ВЫБОР БОНУСА
# =========================================================

@router.callback_query(
    F.data.startswith(
        "ref_bonus_client:"
    )
)
async def referral_bonus_client_selected(
    callback: CallbackQuery,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    if not callback.data:
        return

    try:

        client_id = int(
            callback.data.split(
                ":",
                1,
            )[1]
        )

    except (
        ValueError,
        IndexError,
    ):

        await callback.answer()

        return

    client = get_client_by_id(
        client_id
    )

    if not client:

        await callback.answer(
            "Клиент не найден.",
            show_alert=True,
        )

        return

    if not client["first_visit_paid"]:

        await callback.answer(
            "Первый визит этого клиента "
            "ещё не отмечен как оплаченный.",
            show_alert=True,
        )

        return

    if client["bonus_paid"]:

        await callback.answer(
            "Этот бонус уже отмечен "
            "как выданный.",
            show_alert=True,
        )

        return

    client_name = (
        client["first_name"]
        or "Без имени"
    )

    referrer_name = (
        client["referrer_name"]
        or client["ref_code"]
    )

    if callback.message:

        await callback.message.answer(
            "💰 Подтвердите выдачу бонуса\n\n"
            f"👤 Клиент: {client_name}\n"
            f"🤝 Рекомендатель: "
            f"{referrer_name}\n"
            f"🎁 Сумма бонуса: "
            f"{client['bonus_amount']} ₽\n\n"
            "Вы действительно уже выдали "
            "этот бонус рекомендателю?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Да, бонус выдан",
                            callback_data=(
                                "ref_bonus_confirm:"
                                f"{client_id}"
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="↩️ Отмена",
                            callback_data=(
                                "ref_admin_cancel"
                            ),
                        )
                    ],
                ]
            ),
        )

    await callback.answer()


# =========================================================
# ПОДТВЕРЖДЕНИЕ ВЫДАЧИ БОНУСА
# =========================================================

@router.callback_query(
    F.data.startswith(
        "ref_bonus_confirm:"
    )
)
async def referral_bonus_confirm(
    callback: CallbackQuery,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    if not callback.data:
        return

    try:

        client_id = int(
            callback.data.split(
                ":",
                1,
            )[1]
        )

    except (
        ValueError,
        IndexError,
    ):

        await callback.answer()

        return

    client = get_client_by_id(
        client_id
    )

    if not client:

        await callback.answer(
            "Клиент не найден.",
            show_alert=True,
        )

        return

    if client["bonus_paid"]:

        await callback.answer(
            "Этот бонус уже был выдан.",
            show_alert=True,
        )

        return

    mark_bonus_paid(
        client_id
    )

    client_name = (
        client["first_name"]
        or "Без имени"
    )

    referrer_name = (
        client["referrer_name"]
        or client["ref_code"]
    )

    if callback.message:

        await callback.message.answer(
            "✅ Бонус отмечен как выданный.\n\n"
            f"👤 Клиент: {client_name}\n"
            f"🤝 Рекомендатель: "
            f"{referrer_name}\n"
            f"💰 Выдано: "
            f"{client['bonus_amount']} ₽\n\n"
            "Эта сумма больше не будет "
            "учитываться в разделе "
            "«Осталось выдать».",
            reply_markup=get_referral_admin_menu(),
        )

    await callback.answer(
        "Бонус выдан ✅"
    )


# =========================================================
# ОТМЕНА ДЕЙСТВИЯ
# =========================================================

@router.callback_query(
    F.data == "ref_admin_cancel"
)
async def referral_admin_cancel(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    await state.clear()

    if callback.message:

        await callback.message.answer(
            "🔐 Управление реферальной системой\n\n"
            "Действие отменено. "
            "Выберите, что хотите сделать:",
            reply_markup=get_referral_admin_menu(),
        )

    await callback.answer()


# =========================================================
# START
# =========================================================

@router.message(
    CommandStart()
)
async def command_start(
    message: Message,
    command: CommandObject,
) -> None:

    referral_registered = False

    if command.args:

        start_payload = (
            command.args
            .strip()
        )

        if start_payload.lower().startswith(
            "ref_"
        ):

            ref_code = (
                start_payload[4:]
                .strip()
                .upper()
            )

            if (
                ref_code
                and message.from_user
            ):

                referral_registered = (
                    register_referral_client(
                        platform="telegram",
                        platform_user_id=str(
                            message.from_user.id
                        ),
                        username=(
                            message.from_user.username
                        ),
                        first_name=(
                            message.from_user.first_name
                        ),
                        ref_code=ref_code,
                    )
                )

    await message.answer(
        WELCOME_TEXT,
        reply_markup=get_main_menu(
            is_admin=is_admin_message(
                message
            )
        ),
    )

    if referral_registered:

        await message.answer(
            "🎁 Промокод рекомендации сохранён.\n\n"
            "На первое посещение для вас "
            "действует скидка 10%."
        )


# =========================================================
# УСЛУГИ
# =========================================================

@router.message(
    F.text == "💆 Услуги"
)
async def show_services(
    message: Message,
) -> None:

    await message.answer(
        "💆 Выберите услугу:",
        reply_markup=get_services_menu(),
    )


# =========================================================
# ЦЕНЫ
# =========================================================

@router.message(
    F.text == "💰 Цены"
)
async def show_prices(
    message: Message,
) -> None:

    await message.answer(
        PRICES_TEXT
    )


# =========================================================
# ПОМОЧЬ ВЫБРАТЬ
# =========================================================

@router.message(
    F.text == "🤔 Помочь выбрать"
)
async def help_choose(
    message: Message,
) -> None:

    await message.answer(
        HELP_CHOOSE_TEXT,
        reply_markup=get_help_menu(),
    )


# =========================================================
# ЗАПИСЬ
# =========================================================

@router.message(
    F.text == "📅 Записаться онлайн"
)
async def show_booking(
    message: Message,
) -> None:

    await message.answer(
        "📅 Онлайн-запись\n\n"
        "Выберите удобную дату и время "
        "в сервисе DIKIDI:",
        reply_markup=get_booking_menu(),
    )


# =========================================================
# СЕРТИФИКАТЫ
# =========================================================

@router.message(
    F.text == "🎁 Сертификаты"
)
async def show_certificates(
    message: Message,
) -> None:

    await message.answer(
        CERTIFICATES_TEXT,
        reply_markup=get_question_menu(),
    )


# =========================================================
# ГРУППА
# =========================================================

@router.message(
    F.text == "📢 Вступить в группу"
)
async def show_group(
    message: Message,
) -> None:

    keyboard = get_group_menu()

    if not keyboard.inline_keyboard:

        await message.answer(
            "📢 Ссылка на группу "
            "пока не настроена."
        )

        return

    await message.answer(
        "📢 Вступить в группу можно "
        "по кнопке ниже 👇",
        reply_markup=keyboard,
    )


# =========================================================
# КОНТАКТЫ
# =========================================================

@router.message(
    F.text == "📍 Контакты"
)
async def show_contacts(
    message: Message,
) -> None:

    await message.answer(
        CONTACTS_TEXT,
        reply_markup=get_contacts_menu(),
    )


# =========================================================
# О СПЕЦИАЛИСТЕ
# =========================================================

@router.message(
    F.text == "👩‍⚕️ О специалисте"
)
async def show_about(
    message: Message,
) -> None:

    await message.answer(
        ABOUT_TEXT,
        reply_markup=get_contacts_menu(),
    )


# =========================================================
# ПЕРЕД ВИЗИТОМ
# =========================================================

@router.message(
    F.text == "⚠️ Перед визитом"
)
async def show_before_visit(
    message: Message,
) -> None:

    await message.answer(
        BEFORE_VISIT_TEXT,
        reply_markup=get_question_menu(),
    )


# =========================================================
# ЗАДАТЬ ВОПРОС
# =========================================================

@router.message(
    F.text == "💬 Задать вопрос"
)
async def show_question(
    message: Message,
) -> None:

    await message.answer(
        QUESTION_TEXT,
        reply_markup=get_question_menu(),
    )


# =========================================================
# КАРТОЧКА УСЛУГИ
# =========================================================

@router.callback_query(
    F.data.startswith(
        "service_"
    )
)
async def show_service(
    callback: CallbackQuery,
) -> None:

    if not callback.data:
        return

    service_key = (
        callback.data.removeprefix(
            "service_"
        )
    )

    try:

        text = get_service_text(
            service_key
        )

    except KeyError:

        await callback.answer()

        return

    if callback.message:

        await callback.message.answer(
            text
        )

    await callback.answer()


# =========================================================
# РЕЗУЛЬТАТ "ПОМОЧЬ ВЫБРАТЬ"
# =========================================================

@router.callback_query(
    F.data.startswith(
        "help_"
    )
)
async def show_help_result(
    callback: CallbackQuery,
) -> None:

    if not callback.data:
        return

    help_key = (
        callback.data.removeprefix(
            "help_"
        )
    )

    if help_key == "question":

        if callback.message:

            await callback.message.answer(
                HELP_QUESTION_TEXT,
                reply_markup=get_question_menu(),
            )

        await callback.answer()

        return

    option = HELP_OPTIONS.get(
        help_key
    )

    if not option:

        await callback.answer()

        return

    if callback.message:

        await callback.message.answer(
            option["text"]
        )

    await callback.answer()