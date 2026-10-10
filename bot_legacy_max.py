# ======= ИМПОРТЫ =======

import os
import asyncio
import aiohttp
import hmac
from aiohttp import web
from dotenv import load_dotenv


# ======= НАСТРОЙКИ =======

load_dotenv()

token = os.getenv("MAX_BOT_TOKEN")

API_URL = "https://platform-api2.max.ru"


USE_WEBHOOK = (
    os.getenv("MAX_USE_WEBHOOK", "false").lower() == "true"
)

WEBHOOK_SECRET = os.getenv("MAX_WEBHOOK_SECRET")


if not token:
    raise ValueError("MAX_BOT_TOKEN не найден в файле .env")

print("MAX_BOT_TOKEN загружен")

# ======= ГЛАВНОЕ МЕНЮ =======

def get_main_menu():
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "callback",
                            "text": "💆 Услуги",
                            "payload": "services"
                        },
                        {
                            "type": "callback",
                            "text": "💰 Цены",
                            "payload": "prices"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "🤔 Помочь выбрать",
                            "payload": "help_choose"
                        },
                        {
                            "type": "link",
                            "text": "📅 Записаться онлайн",
                            "url": "https://dikidi.ru/1646575"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "🎁 Сертификаты",
                            "payload": "certificates"
                        },
                        {
                            "type": "link",
                            "text": "📢 Подписаться на канал",
                            "url": "https://max.ru/channel_as_estetik"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "📍 Контакты",
                            "payload": "contacts"
                        },
                        {
                            "type": "callback",
                            "text": "👩‍⚕️ О специалисте",
                            "payload": "about"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "⚠️ Перед визитом",
                            "payload": "before_visit"
                        },
                        {
                            "type": "callback",
                            "text": "💬 Задать вопрос",
                            "payload": "question"
                        }
                    ]
                ]
            }
        }
    ]


# ======= ОТПРАВКА СООБЩЕНИЙ =======

async def send_message(chat_id, text, attachments=None):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text
    }

    if attachments:
        payload["attachments"] = attachments

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            f"{API_URL}/messages",
            params={"chat_id": chat_id},
            json=payload
        ) as response:
            data = await response.json()

            if response.status != 200:
                print(
                    "Ошибка отправки сообщения:",
                    response.status,
                    data
                )

            return data


# ======= ОБРАБОТКА СОБЫТИЙ MAX =======

# ======= МЕНЮ УСЛУГ =======

def get_services_menu():
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "callback",
                            "text": "💆 Общий оздоровительный",
                            "payload": "service_general"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "💆 Массаж спины",
                            "payload": "service_back"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "✨ Пластический массаж лица",
                            "payload": "service_face"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "👣 Массаж стоп",
                            "payload": "service_feet"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "🔥 Антицеллюлитный",
                            "payload": "service_anticellulite"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "🌿 Висцеральный",
                            "payload": "service_visceral"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "⬅️ Главное меню",
                            "payload": "back_main"
                        }
                    ]
                ]
            }
        }
    ]



# ======= КНОПКИ В КАРТОЧКЕ УСЛУГИ =======

def get_service_card_menu():
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "link",
                            "text": "📅 Записаться онлайн",
                            "url": "https://dikidi.ru/1646575"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "⬅️ К услугам",
                            "payload": "services"
                        }
                    ]
                ]
            }
        }
    ]

# ======= МЕНЮ "ПОМОЧЬ ВЫБРАТЬ" =======

def get_help_choose_menu():
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "callback",
                            "text": "😌 Расслабить всё тело",
                            "payload": "help_general"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "💆 Спина и шея",
                            "payload": "help_back"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "✨ Лицо",
                            "payload": "help_face"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "👣 Стопы",
                            "payload": "help_feet"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "🔥 Силуэт",
                            "payload": "help_anticellulite"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "🌿 Область живота",
                            "payload": "help_visceral"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "❓ Не знаю / хочу спросить",
                            "payload": "help_question"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "⬅️ Главное меню",
                            "payload": "back_main"
                        }
                    ]
                ]
            }
        }
    ]


# ======= КНОПКИ ПОСЛЕ РЕКОМЕНДАЦИИ =======

def get_help_result_menu():
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "link",
                            "text": "📅 Записаться онлайн",
                            "url": "https://dikidi.ru/1646575"
                        }
                    ],
                    [
                        {
                            "type": "callback",
                            "text": "⬅️ Назад к выбору",
                            "payload": "help_choose"
                        }
                    ]
                ]
            }
        }
    ]

# ======= ОТВЕТ НА CALLBACK =======

async def answer_callback(
    session,
    callback_id,
    text,
    attachments=None
):
    params = {
        "callback_id": callback_id
    }

    message = {
        "text": text
    }

    if attachments:
        message["attachments"] = attachments

    body = {
        "message": message
    }

    async with session.post(
        f"{API_URL}/answers",
        params=params,
        json=body
    ) as response:
        data = await response.json()

        if response.status != 200:
            print(
                "Ошибка callback:",
                response.status,
                data
            )


# ======= ОБРАБОТКА КНОПОК =======

async def handle_callback(session, update):
    callback = update.get("callback", {})

    callback_id = callback.get("callback_id")
    payload = callback.get("payload")

    if not callback_id:
        return

    print("Нажата кнопка:", payload)

    if payload == "help_choose":
        await answer_callback(
            session,
            callback_id,
            "🤔 Что вас сейчас интересует больше всего?",
            attachments=get_help_choose_menu()
        )

    elif payload == "help_general":
        await answer_callback(
            session,
            callback_id,
            "😌 Если хочется расслабить всё тело\n\n"
            "Рекомендую общий оздоровительный массаж.\n\n"
            "💆 Комплексная работа с телом помогает снять "
            "мышечное напряжение и почувствовать лёгкость.\n\n"
            "⏱ 1 ч 15 мин\n"
            "💰 2500 ₽",
            attachments=get_help_result_menu()
        )

    elif payload == "help_back":
        await answer_callback(
            session,
            callback_id,
            "💆 Если беспокоят спина и шея\n\n"
            "Рекомендую оздоровительный массаж спины.\n\n"
            "Работа с поясничным, грудным и шейным отделами, "
            "а также небольшой массаж головы.\n\n"
            "Подходит при усталости, скованности и мышечном напряжении.\n\n"
            "⏱ 45 мин\n"
            "💰 2000 ₽",
            attachments=get_help_result_menu()
        )

    elif payload == "help_face":
        await answer_callback(
            session,
            callback_id,
            "✨ Если хочется уделить внимание лицу\n\n"
            "Рекомендую пластический массаж лица.\n\n"
            "Ручной массаж с акцентом на расслабление напряжённых мышц, "
            "тонус тканей и уход за кожей.\n\n"
            "⏱ 45 мин\n"
            "💰 2000 ₽",
            attachments=get_help_result_menu()
        )

    elif payload == "help_feet":
        await answer_callback(
            session,
            callback_id,
            "👣 Если устали или напряжены стопы\n\n"
            "Рекомендую артикуляционно-рефлекторный массаж стоп.\n\n"
            "Работа со стопами, их подвижностью и рефлекторными зонами.\n\n"
            "Подходит при усталости и напряжении стоп.\n\n"
            "⏱ 1 ч 40 мин\n"
            "💰 2700 ₽",
            attachments=get_help_result_menu()
        )

    elif payload == "help_anticellulite":
        await answer_callback(
            session,
            callback_id,
            "🔥 Если хочется поработать с силуэтом\n\n"
            "Рекомендую антицеллюлитный массаж.\n\n"
            "Интенсивная ручная работа с проблемными зонами и силуэтом. "
            "Интенсивность подбирается индивидуально.\n\n"
            "Для более выраженного результата часто рекомендуется курс процедур.\n\n"
            "⏱ 1 ч 15 мин\n"
            "💰 2500 ₽",
            attachments=get_help_result_menu()
        )

    elif payload == "help_visceral":
        await answer_callback(
            session,
            callback_id,
            "🌿 Если хочется уделить внимание области живота\n\n"
            "Возможно, подойдёт висцеральный массаж.\n\n"
            "Это ручная работа с областью живота с учётом "
            "чувствительности и самочувствия.\n\n"
            "Перед процедурой важно сообщить специалисту "
            "о хронических заболеваниях и перенесённых операциях.\n\n"
            "⏱ 45 мин\n"
            "💰 2000 ₽",
            attachments=get_help_result_menu()
        )

    elif payload == "help_question":
        await answer_callback(
            session,
            callback_id,
            "❓ Не уверены, какой массаж выбрать?\n\n"
            "Напишите мне — помогу сориентироваться по услугам "
            "и отвечу на ваши вопросы 😊",
            attachments=[
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "link",
                                    "text": "💬 Написать в MAX",
                                    "url": "https://max.ru/u/f9LHodD0cOICGGngPNgwNXPPKw-2thwyF_zBbcG1E6ID6TBU204vm10393A"
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "⬅️ Назад к выбору",
                                    "payload": "help_choose"
                                }
                            ]
                        ]
                    }
                }
            ]
        )

    elif payload == "certificates":
        await answer_callback(
            session,
            callback_id,
            "🎁 Подарочные сертификаты и абонементы\n\n"
            "Сертификат можно оформить:\n"
            "• на конкретный вид массажа\n"
            "• на любую выбранную сумму\n\n"
            "Абонементы:\n"
            "от 5 сеансов — скидка 10%.\n\n"
            "В одном абонементе можно сочетать разные виды массажа.\n\n"
            "Для оформления напишите мне удобным способом 😊",
            attachments=[
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "link",
                                    "text": "💬 Написать в MAX",
                                    "url": "https://max.ru/u/f9LHodD0cOICGGngPNgwNXPPKw-2thwyF_zBbcG1E6ID6TBU204vm10393A"
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "⬅️ Главное меню",
                                    "payload": "back_main"
                                }
                            ]
                        ]
                    }
                }
            ]
        )


    elif payload == "contacts":
        await answer_callback(
            session,
            callback_id,
            "📍 Контакты As_estetik\n\n"
            "📌 Краснодар, ул. Мачуги, 41\n"
            "4 этаж, кабинет массажа\n\n"
            "📞 8 (918) 097-72-87\n\n"
            "Приём — по предварительной записи.\n\n"
            "Связаться со мной можно в MAX 👇",
            attachments=[
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "link",
                                    "text": "📅 Записаться онлайн",
                                    "url": "https://dikidi.ru/1646575"
                                }
                            ],
                            [
                                {
                                    "type": "link",
                                    "text": "💬 Написать в MAX",
                                    "url": "https://max.ru/u/f9LHodD0cOICGGngPNgwNXPPKw-2thwyF_zBbcG1E6ID6TBU204vm10393A"
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "⬅️ Главное меню",
                                    "payload": "back_main"
                                }
                            ]
                        ]
                    }
                }
            ]
        )


    elif payload == "about":
        await answer_callback(
            session,
            callback_id,
            "👩‍⚕️ О специалисте\n\n"
            "Меня зовут Алла.\n\n"
            "Я дипломированный массажист с медицинским образованием. "
            "Опыт работы — более 8 лет.\n\n"
            "В работе для меня важны индивидуальный подход, комфорт клиента "
            "и внимательное отношение к самочувствию.\n\n"
            "Приём веду по предварительной записи в Краснодаре 🌿",
            attachments=[
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "link",
                                    "text": "📅 Записаться онлайн",
                                    "url": "https://dikidi.ru/1646575"
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "⬅️ Главное меню",
                                    "payload": "back_main"
                                }
                            ]
                        ]
                    }
                }
            ]
        )


    elif payload == "before_visit":
        await answer_callback(
            session,
            callback_id,
            "⚠️ Важно перед посещением\n\n"
            "Массаж лучше перенести или предварительно проконсультироваться, если есть:\n\n"
            "• температура или острое инфекционное заболевание\n"
            "• острое воспаление или сильная боль неясного происхождения\n"
            "• открытые раны, ожоги или выраженные кожные воспаления в зоне массажа\n"
            "• кровотечение или высокий риск кровотечения\n"
            "• тромбоз, тромбофлебит или подозрение на них\n"
            "• недавняя операция, свежая травма или перелом\n"
            "• выраженное обострение сердечно-сосудистого или другого хронического заболевания\n\n"
            "Обязательно сообщите, если вы беременны, принимаете препараты, "
            "влияющие на свёртываемость крови, проходите онкологическое лечение "
            "или имеете серьёзные хронические заболевания.\n\n"
            "Если есть сомнения, лучше заранее написать мне 🌿",
            attachments=[
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "link",
                                    "text": "💬 Написать в MAX",
                                    "url": "https://max.ru/u/f9LHodD0cOICGGngPNgwNXPPKw-2thwyF_zBbcG1E6ID6TBU204vm10393A"
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "⬅️ Главное меню",
                                    "payload": "back_main"
                                }
                            ]
                        ]
                    }
                }
            ]
        )


    elif payload == "question":
        await answer_callback(
            session,
            callback_id,
            "💬 Задать вопрос\n\n"
            "Если у вас есть вопрос по массажу, выбору процедуры, "
            "подготовке к визиту или записи — напишите мне в MAX.\n\n"
            "Я отвечу и помогу разобраться 🌿",
            attachments=[
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "link",
                                    "text": "💬 Написать в MAX",
                                    "url": "https://max.ru/u/f9LHodD0cOICGGngPNgwNXPPKw-2thwyF_zBbcG1E6ID6TBU204vm10393A"
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "⬅️ Главное меню",
                                    "payload": "back_main"
                                }
                            ]
                        ]
                    }
                }
            ]
        )

    elif payload == "prices":

        await answer_callback(
            session,
            callback_id,
            "💰 Прайс As_estetik\n\n"
            "💆 Общий оздоровительный массаж\n"
            "1 ч 15 мин — 2500 ₽\n\n"
            "💆 Оздоровительный массаж спины\n"
            "45 мин — 2000 ₽\n\n"
            "✨ Пластический массаж лица\n"
            "45 мин — 2000 ₽\n\n"
            "👣 Артикуляционно-рефлекторный массаж стоп\n"
            "1 ч 40 мин — 2700 ₽\n\n"
            "🔥 Антицеллюлитный массаж\n"
            "1 ч 15 мин — 2500 ₽\n\n"
            "🌿 Висцеральный массаж\n"
            "45 мин — 2000 ₽",
                       attachments=[
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "callback",
                                    "text": "⬅️ Главное меню",
                                    "payload": "back_main"
                                }
                            ]
                        ]
                    }
                }
            ]
        )



    elif payload == "services":
        await answer_callback(
            session,
            callback_id,
            "💆 Выберите услугу:",
            attachments=get_services_menu()
        )

    elif payload == "service_general":
        await answer_callback(
            session,
            callback_id,
            "💆 Общий оздоровительный массаж\n\n"
            "Комплексная работа с телом, направленная на расслабление, "
            "снижение мышечного напряжения и ощущение лёгкости.\n\n"
            "⏱ 1 ч 15 мин\n"
            "💰 2500 ₽",
            attachments=get_service_card_menu()
        )

    elif payload == "service_back":
        await answer_callback(
            session,
            callback_id,
            "💆 Оздоровительный массаж спины\n\n"
            "Работа с поясничным, грудным и шейным отделами, "
            "а также небольшой массаж головы.\n\n"
            "Подходит при усталости, скованности и мышечном напряжении.\n\n"
            "⏱ 45 мин\n"
            "💰 2000 ₽",
            attachments=get_service_card_menu()
        )

    elif payload == "service_face":
        await answer_callback(
            session,
            callback_id,
            "✨ Пластический массаж лица\n\n"
            "Ручной массаж лица с акцентом на расслабление напряжённых мышц, "
            "тонус тканей и уход за кожей.\n\n"
            "⏱ 45 мин\n"
            "💰 2000 ₽",
            attachments=get_service_card_menu()
        )

    elif payload == "service_feet":
        await answer_callback(
            session,
            callback_id,
            "👣 Артикуляционно-рефлекторный массаж стоп\n\n"
            "Работа со стопами, их подвижностью и рефлекторными зонами.\n\n"
            "Подходит при усталости и напряжении стоп.\n\n"
            "⏱ 1 ч 40 мин\n"
            "💰 2700 ₽",
            attachments=get_service_card_menu()
        )

    elif payload == "service_anticellulite":
        await answer_callback(
            session,
            callback_id,
            "🔥 Антицеллюлитный массаж\n\n"
            "Интенсивная ручная работа с проблемными зонами и силуэтом.\n\n"
            "Интенсивность подбирается индивидуально. "
            "Для более выраженного результата часто рекомендуется курс процедур.\n\n"
            "⏱ 1 ч 15 мин\n"
            "💰 2500 ₽",
            attachments=get_service_card_menu()
        )

    elif payload == "service_visceral":
        await answer_callback(
            session,
            callback_id,
            "🌿 Висцеральный массаж\n\n"
            "Ручная работа с областью живота с учётом чувствительности "
            "и самочувствия.\n\n"
            "Перед процедурой важно сообщить специалисту о хронических "
            "заболеваниях и перенесённых операциях.\n\n"
            "⏱ 45 мин\n"
            "💰 2000 ₽",
            attachments=get_service_card_menu()
        )

    elif payload == "back_main":
        await answer_callback(
            session,
            callback_id,
            "🌿 Главное меню As_estetik\n\n"
            "Выберите нужный раздел 👇",
            attachments=get_main_menu()
        )


async def max_webhook_handler(request):
    if not WEBHOOK_SECRET:
        print("MAX_WEBHOOK_SECRET не настроен")
        return web.Response(
            status=500,
            text="Webhook secret is not configured"
        )

    received_secret = request.headers.get(
        "X-Max-Bot-Api-Secret",
        ""
    )

    if not hmac.compare_digest(
        received_secret,
        WEBHOOK_SECRET
    ):
        print("Неверный секрет MAX webhook")
        return web.Response(
            status=401,
            text="Unauthorized"
        )

    try:
        update = await request.json()
        update_type = update.get("update_type")

        print(
            "Получено MAX webhook событие:",
            update_type
        )

        headers = {
            "Authorization": token
        }

        async with aiohttp.ClientSession(
            headers=headers
        ) as session:

            if update_type == "bot_started":
                chat_id = update.get("chat_id")

                if chat_id:
                    await send_message(
                        chat_id,
                        "Здравствуйте! Добро пожаловать в As_estetik 🌿",
                        attachments=get_main_menu()
                    )

            elif update_type == "message_created":
                message = update.get("message", {})
                body = message.get("body", {})
                text = body.get("text", "")

                chat_id = message.get(
                    "recipient",
                    {}
                ).get("chat_id")

                if text == "/start" and chat_id:
                    await send_message(
                        chat_id,
                        "Здравствуйте! Добро пожаловать в As_estetik 🌿",
                        attachments=get_main_menu()
                    )

            elif update_type == "message_callback":
                await handle_callback(
                    session,
                    update
                )

    except Exception as error:
        print(
            "Ошибка MAX webhook:",
            error
        )
        return web.Response(
            status=500,
            text="Webhook error"
        )

    return web.Response(
        status=200,
        text="OK"
    )

# ======= ОБРАБОТКА СОБЫТИЙ MAX =======

async def main():
    headers = {
        "Authorization": token
    }

    if USE_WEBHOOK:
        app = web.Application()

        app.router.add_post(
            "/max/webhook",
            max_webhook_handler
        )

        runner = web.AppRunner(app)
        await runner.setup()

        port = int(
            os.getenv("PORT", "8080")
        )

        site = web.TCPSite(
            runner,
            "0.0.0.0",
            port
        )

        await site.start()

        print(
            f"MAX webhook сервер запущен на порту {port}"
        )
        print(
            "As_estetik работает в режиме WEBHOOK"
        )

        while True:
            await asyncio.sleep(3600)

    marker = None

    async with aiohttp.ClientSession(headers=headers) as session:
        print("As_estetik запущен и ждёт события...")

        async with session.get(
            f"{API_URL}/updates",
            params={
                "timeout": 0,
                "limit": 1,
                "types": "bot_started,message_created,message_callback"
            }
        ) as response:
            initial_data = await response.json()

        marker = initial_data.get("marker")

        while True:
            try:
                params = {
                    "timeout": 30,
                    "types": "bot_started,message_created,message_callback"
                }

                if marker is not None:
                    params["marker"] = marker

                async with session.get(
                    f"{API_URL}/updates",
                    params=params
                ) as response:
                    data = await response.json()

                new_marker = data.get("marker")

                if new_marker is not None:
                    marker = new_marker

                for update in data.get("updates", []):
                    update_type = update.get("update_type")

                    if update_type == "bot_started":
                        chat_id = update.get("chat_id")

                        if chat_id:
                            await send_message(
                                chat_id,
                                "Здравствуйте! Добро пожаловать в As_estetik 🌿",
                                attachments=get_main_menu()
                            )

                    elif update_type == "message_created":
                        message = update.get("message", {})
                        body = message.get("body", {})
                        text = body.get("text", "")
                        chat_id = message.get(
                            "recipient",
                            {}
                        ).get("chat_id")

                        if text == "/start" and chat_id:
                            await send_message(
                                chat_id,
                                "Здравствуйте! Добро пожаловать в As_estetik 🌿",
                                attachments=get_main_menu()
                            )

                    elif update_type == "message_callback":
                        await handle_callback(
                            session,
                            update
                        )

            except Exception as error:
                print("Ошибка:", error)
                await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())




































