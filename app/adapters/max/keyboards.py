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


def get_main_menu() -> list:
    return inline_keyboard(
        [
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
    )


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