import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.filters.command import CommandObject
from aiogram.types import CallbackQuery, Message

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
    get_referral_summary,
    register_referral_client,
)


router = Router()


TELEGRAM_ADMIN_ID = os.getenv(
    "TELEGRAM_ADMIN_ID"
)


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
# MY ID
# =========================================================

@router.message(Command("myid"))
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
# ДОБАВИТЬ РЕФЕРАЛЬНЫЙ КОД
# ТЕХНИЧЕСКАЯ КОМАНДА
# =========================================================

@router.message(Command("ref_add"))
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
        "✅ Реферальный код создан.\n\n"
        f"Имя: {name}\n"
        f"Код: {code}\n\n"
        "Ссылка на сайт:\n"
        f"https://as-estetik.ru/?ref={code}"
    )


# =========================================================
# СТАТИСТИКА — ТЕКСТ
# =========================================================

def build_referral_stats_text() -> str:

    rows = get_referral_summary()

    if not rows:
        return (
            "📊 Реферальная статистика\n\n"
            "Реферальных кодов пока нет."
        )

    lines = [
        "📊 Реферальная статистика"
    ]

    for row in rows:

        lines.append(
            "\n"
            f"👤 {row['name']}\n"
            f"Код: {row['code']}\n"
            f"Приведено: {row['clients_count']}\n"
            f"Оплатили: {row['paid_clients_count']}\n"
            f"Бонус всего: {row['total_bonus']} ₽\n"
            f"К выплате: {row['bonus_to_pay']} ₽"
        )

    return "\n".join(lines)


# =========================================================
# КЛИЕНТЫ — ТЕКСТ
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

        username = (
            f"@{row['username']}"
            if row["username"]
            else "без username"
        )

        first_name = (
            row["first_name"]
            or "Имя не указано"
        )

        referrer_name = (
            row["referrer_name"]
            or "Неизвестно"
        )

        paid_status = (
            "✅ оплачен"
            if row["first_visit_paid"]
            else "⏳ не оплачен"
        )

        bonus_status = (
            "✅ выдан"
            if row["bonus_paid"]
            else "⏳ не выдан"
        )

        lines.append(
            "\n"
            f"#{row['id']} — {first_name}\n"
            f"{username}\n"
            f"Код: {row['ref_code']}\n"
            f"Рекомендатель: {referrer_name}\n"
            f"Платформа: {row['platform']}\n"
            f"Первый визит: {paid_status}\n"
            f"Бонус: {row['bonus_amount']} ₽\n"
            f"Бонус рекомендателю: {bonus_status}"
        )

    if len(rows) > 20:

        lines.append(
            "\nПоказаны последние 20 клиентов."
        )

    return "\n".join(lines)


# =========================================================
# ТЕХНИЧЕСКИЕ КОМАНДЫ СТАТИСТИКИ
# =========================================================

@router.message(Command("ref_stats"))
async def ref_stats(
    message: Message,
) -> None:

    if not is_admin_message(message):
        return

    await message.answer(
        build_referral_stats_text()
    )


@router.message(Command("ref_clients"))
async def ref_clients(
    message: Message,
) -> None:

    if not is_admin_message(message):
        return

    await message.answer(
        build_referral_clients_text()
    )


# =========================================================
# АДМИН-ПАНЕЛЬ РЕФЕРАЛОВ
# =========================================================

@router.message(
    F.text == "🔐 Рефералы"
)
async def show_referral_admin(
    message: Message,
) -> None:

    if not is_admin_message(message):
        return

    await message.answer(
        "🔐 Управление реферальной системой\n\n"
        "Выберите действие:",
        reply_markup=get_referral_admin_menu(),
    )


# =========================================================
# АДМИН — СТАТИСТИКА
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
# АДМИН — КЛИЕНТЫ
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
# ВРЕМЕННЫЕ ОБРАБОТЧИКИ ОСТАЛЬНЫХ КНОПОК
# =========================================================

@router.callback_query(
    F.data.in_(
        {
            "ref_admin_add",
            "ref_admin_paid",
            "ref_admin_bonus",
        }
    )
)
async def referral_admin_next_steps(
    callback: CallbackQuery,
) -> None:

    if not is_admin_callback(callback):

        await callback.answer()

        return

    await callback.answer(
        "Эту кнопку подключаем следующим шагом.",
        show_alert=True,
    )


# =========================================================
# START
# =========================================================

@router.message(CommandStart())
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
            "На первое посещение для вас действует "
            "скидка 10%."
        )


# =========================================================
# УСЛУГИ
# =========================================================

@router.message(F.text == "💆 Услуги")
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

@router.message(F.text == "💰 Цены")
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
            "📢 Ссылка на группу пока "
            "не настроена."
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

@router.message(F.text == "📍 Контакты")
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
# ВОПРОС
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
    F.data.startswith("service_")
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
    F.data.startswith("help_")
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