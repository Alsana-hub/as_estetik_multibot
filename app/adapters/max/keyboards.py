from app.core.content import (
    DIKIDI_URL,
    MAX_CHANNEL_URL,
    MAX_CONTACT_URL,
    HELP_OPTIONS,
    SERVICES,
)


def inline_keyboard(
    rows: list[list[dict]],
) -> list:
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": rows,
            },
        }
    ]


def callback_button(
    text: str,
    payload: str,
) -> dict:
    return {
        "type": "callback",
        "text": text,
        "payload": payload,
    }


def link_button(
    text: str,
    url: str,
) -> dict:
    return {
        "type": "link",
        "text": text,
        "url": url,
    }


# =========================================================
# ГЛАВНОЕ МЕНЮ
# =========================================================

def get_main_menu(
    is_admin: bool = False,
) -> list:

    rows = [
        [
            callback_button(
                "💆 Услуги",
                "services",
            ),
            callback_button(
                "💰 Цены",
                "prices",
            ),
        ],
        [
            callback_button(
                "🤔 Помочь выбрать",
                "help_choose",
            ),
            link_button(
                "📅 Записаться онлайн",
                DIKIDI_URL,
            ),
        ],
        [
            callback_button(
                "🎁 Сертификаты",
                "certificates",
            ),
            link_button(
                "📢 Подписаться на канал",
                MAX_CHANNEL_URL,
            ),
        ],
        [
            callback_button(
                "📍 Контакты",
                "contacts",
            ),
            callback_button(
                "👩‍⚕️ О специалисте",
                "about",
            ),
        ],
        [
            callback_button(
                "⚠️ Перед визитом",
                "before_visit",
            ),
            callback_button(
                "💬 Задать вопрос",
                "question",
            ),
        ],
    ]

    if is_admin:
        rows.append(
            [
                callback_button(
                    "🔐 Рефералы",
                    "ref_admin",
                )
            ]
        )

    return inline_keyboard(rows)


# =========================================================
# РЕФЕРАЛЬНАЯ АДМИН-ПАНЕЛЬ
# =========================================================

def get_referral_admin_menu() -> list:
    return inline_keyboard(
        [
            [
                callback_button(
                    "➕ Добавить партнёра",
                    "ref_admin_add",
                )
            ],
            [
                callback_button(
                    "📊 Статистика",
                    "ref_admin_stats",
                )
            ],
            [
                callback_button(
                    "👥 Клиенты",
                    "ref_admin_clients",
                )
            ],
            [
                callback_button(
                    "✅ Отметить оплату",
                    "ref_admin_paid",
                )
            ],
            [
                callback_button(
                    "💰 Бонус выдан",
                    "ref_admin_bonus",
                )
            ],
            [
                callback_button(
                    "⬅️ Главное меню",
                    "back_main",
                )
            ],
        ]
    )


def get_referral_unpaid_clients_menu(
    rows,
) -> list:

    buttons = []

    for row in rows:

        first_name = (
            row["first_name"]
            or "Без имени"
        )

        referrer = (
            row["referrer_name"]
            or row["ref_code"]
            or "—"
        )

        buttons.append(
            [
                callback_button(
                    (
                        f"Клиент: {first_name} | "
                        f"Рекомендатель: {referrer}"
                    ),
                    f"ref_paid_client:{row['id']}",
                )
            ]
        )

    buttons.append(
        [
            callback_button(
                "↩️ Отмена",
                "ref_admin_cancel",
            )
        ]
    )

    return inline_keyboard(buttons)


def get_referral_bonus_clients_menu(
    rows,
) -> list:

    buttons = []

    for row in rows:

        first_name = (
            row["first_name"]
            or "Без имени"
        )

        referrer = (
            row["referrer_name"]
            or row["ref_code"]
            or "—"
        )

        buttons.append(
            [
                callback_button(
                    (
                        f"Клиент: {first_name} | "
                        f"Рекомендатель: {referrer} | "
                        f"{row['bonus_amount']} ₽"
                    ),
                    f"ref_bonus_client:{row['id']}",
                )
            ]
        )

    buttons.append(
        [
            callback_button(
                "↩️ Отмена",
                "ref_admin_cancel",
            )
        ]
    )

    return inline_keyboard(buttons)


def get_referral_bonus_confirm_menu(
    client_id: int,
) -> list:

    return inline_keyboard(
        [
            [
                callback_button(
                    "✅ Да, бонус выдан",
                    f"ref_bonus_confirm:{client_id}",
                )
            ],
            [
                callback_button(
                    "↩️ Отмена",
                    "ref_admin_cancel",
                )
            ],
        ]
    )


# =========================================================
# УСЛУГИ
# =========================================================

def get_services_menu() -> list:
    rows = []

    for key, service in SERVICES.items():
        rows.append(
            [
                callback_button(
                    service["menu_title"],
                    f"service_{key}",
                )
            ]
        )

    rows.append(
        [
            callback_button(
                "⬅️ Главное меню",
                "back_main",
            )
        ]
    )

    return inline_keyboard(rows)


def get_service_card_menu() -> list:
    return inline_keyboard(
        [
            [
                link_button(
                    "📅 Записаться онлайн",
                    DIKIDI_URL,
                )
            ],
            [
                callback_button(
                    "⬅️ К услугам",
                    "services",
                )
            ],
        ]
    )


# =========================================================
# ПОМОЧЬ ВЫБРАТЬ
# =========================================================

def get_help_choose_menu() -> list:
    rows = []

    for key, option in HELP_OPTIONS.items():
        rows.append(
            [
                callback_button(
                    option["menu_title"],
                    f"help_{key}",
                )
            ]
        )

    rows.append(
        [
            callback_button(
                "❓ Не знаю / хочу спросить",
                "help_question",
            )
        ]
    )

    rows.append(
        [
            callback_button(
                "⬅️ Главное меню",
                "back_main",
            )
        ]
    )

    return inline_keyboard(rows)


def get_help_result_menu() -> list:
    return inline_keyboard(
        [
            [
                link_button(
                    "📅 Записаться онлайн",
                    DIKIDI_URL,
                )
            ],
            [
                callback_button(
                    "⬅️ Назад к выбору",
                    "help_choose",
                )
            ],
        ]
    )


# =========================================================
# КОНТАКТЫ
# =========================================================

def get_contact_menu() -> list:
    return inline_keyboard(
        [
            [
                link_button(
                    "📅 Записаться онлайн",
                    DIKIDI_URL,
                )
            ],
            [
                link_button(
                    "💬 Написать в MAX",
                    MAX_CONTACT_URL,
                )
            ],
            [
                callback_button(
                    "⬅️ Главное меню",
                    "back_main",
                )
            ],
        ]
    )


def get_write_max_menu() -> list:
    return inline_keyboard(
        [
            [
                link_button(
                    "💬 Написать в MAX",
                    MAX_CONTACT_URL,
                )
            ],
            [
                callback_button(
                    "⬅️ Главное меню",
                    "back_main",
                )
            ],
        ]
    )


def get_about_menu() -> list:
    return inline_keyboard(
        [
            [
                link_button(
                    "📅 Записаться онлайн",
                    DIKIDI_URL,
                )
            ],
            [
                callback_button(
                    "⬅️ Главное меню",
                    "back_main",
                )
            ],
        ]
    )


def get_back_main_menu() -> list:
    return inline_keyboard(
        [
            [
                callback_button(
                    "⬅️ Главное меню",
                    "back_main",
                )
            ]
        ]
    )