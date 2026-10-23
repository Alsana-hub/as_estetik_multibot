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
    register_referral_client,
)


router = Router()


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

            if ref_code:

                referral_registered = (
                    register_referral_client(
                        platform="telegram",
                        platform_user_id=str(
                            message.from_user.id
                        ),
                        username=(
                            message.from_user.username
                            if message.from_user
                            else None
                        ),
                        first_name=(
                            message.from_user.first_name
                            if message.from_user
                            else None
                        ),
                        ref_code=ref_code,
                    )
                )

    await message.answer(
        WELCOME_TEXT,
        reply_markup=get_main_menu(),
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

    await callback.message.answer(
        option["text"]
    )

    await callback.answer()