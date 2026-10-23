import os

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.core.content import (
    DIKIDI_URL,
    HELP_OPTIONS,
    MAX_CONTACT_URL,
    SERVICES,
)


TELEGRAM_CONTACT_URL = "https://t.me/ALLOCHKALIFE"

TELEGRAM_GROUP_URL = os.getenv(
    "TELEGRAM_GROUP_URL",
    "",
)


# =========================================================
# ГЛАВНОЕ МЕНЮ
# =========================================================

def get_main_menu(
    is_admin: bool = False,
) -> ReplyKeyboardMarkup:

    keyboard = [
        [
            KeyboardButton(
                text="💆 Услуги",
            ),
            KeyboardButton(
                text="💰 Цены",
            ),
        ],
        [
            KeyboardButton(
                text="🤔 Помочь выбрать",
            ),
            KeyboardButton(
                text="📅 Записаться онлайн",
            ),
        ],
        [
            KeyboardButton(
                text="🎁 Сертификаты",
            ),
            KeyboardButton(
                text="📢 Вступить в группу",
            ),
        ],
        [
            KeyboardButton(
                text="📍 Контакты",
            ),
            KeyboardButton(
                text="👩‍⚕️ О специалисте",
            ),
        ],
        [
            KeyboardButton(
                text="⚠️ Перед визитом",
            ),
            KeyboardButton(
                text="💬 Задать вопрос",
            ),
        ],
    ]

    if is_admin:
        keyboard.append(
            [
                KeyboardButton(
                    text="🔐 Рефералы",
                )
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


# =========================================================
# АДМИН-ПАНЕЛЬ РЕФЕРАЛОВ
# =========================================================

def get_referral_admin_menu() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить партнёра",
                    callback_data="ref_admin_add",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="ref_admin_stats",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Клиенты",
                    callback_data="ref_admin_clients",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Отметить оплату",
                    callback_data="ref_admin_paid",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Бонус выдан",
                    callback_data="ref_admin_bonus",
                )
            ],
        ]
    )


# =========================================================
# УСЛУГИ
# =========================================================

def get_services_menu() -> InlineKeyboardMarkup:

    buttons = []

    for key, service in SERVICES.items():

        buttons.append(
            [
                InlineKeyboardButton(
                    text=service["menu_title"],
                    callback_data=f"service_{key}",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# =========================================================
# ПОМОЧЬ ВЫБРАТЬ
# =========================================================

def get_help_menu() -> InlineKeyboardMarkup:

    buttons = []

    for key, option in HELP_OPTIONS.items():

        buttons.append(
            [
                InlineKeyboardButton(
                    text=option["menu_title"],
                    callback_data=f"help_{key}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="❓ Не знаю / хочу спросить",
                callback_data="help_question",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# =========================================================
# ЗАДАТЬ ВОПРОС
# =========================================================

def get_question_menu() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Написать в Telegram",
                    url=TELEGRAM_CONTACT_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Написать в MAX",
                    url=MAX_CONTACT_URL,
                )
            ],
        ]
    )


# =========================================================
# ЗАПИСЬ
# =========================================================

def get_booking_menu() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Открыть онлайн-запись",
                    url=DIKIDI_URL,
                )
            ]
        ]
    )


# =========================================================
# КОНТАКТЫ
# =========================================================

def get_contacts_menu() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Записаться онлайн",
                    url=DIKIDI_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Написать в Telegram",
                    url=TELEGRAM_CONTACT_URL,
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Написать в MAX",
                    url=MAX_CONTACT_URL,
                )
            ],
        ]
    )


# =========================================================
# ГРУППА
# =========================================================

def get_group_menu() -> InlineKeyboardMarkup:

    if not TELEGRAM_GROUP_URL:

        return InlineKeyboardMarkup(
            inline_keyboard=[]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Вступить в группу",
                    url=TELEGRAM_GROUP_URL,
                )
            ]
        ]
    )