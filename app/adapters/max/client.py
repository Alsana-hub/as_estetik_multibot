import aiohttp


class MaxClient:
    BASE_URL = "https://platform-api2.max.ru"

    def __init__(
        self,
        token: str,
    ) -> None:
        self.token = token

    def _headers(self) -> dict:
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }

    async def send_message(
        self,
        *,
        chat_id: int,
        text: str,
        attachments: list | None = None,
    ) -> dict:
        payload = {
            "text": text,
        }

        if attachments:
            payload["attachments"] = attachments

        async with aiohttp.ClientSession(
            headers=self._headers()
        ) as session:
            async with session.post(
                f"{self.BASE_URL}/messages",
                params={
                    "chat_id": chat_id,
                },
                json=payload,
            ) as response:
                data = await response.json()

                if response.status != 200:
                    raise RuntimeError(
                        "Ошибка отправки MAX сообщения: "
                        f"{response.status} {data}"
                    )

                return data

    async def answer_callback(
        self,
        *,
        callback_id: str,
        text: str,
        attachments: list | None = None,
    ) -> dict:
        message = {
            "text": text,
        }

        if attachments:
            message["attachments"] = attachments

        body = {
            "message": message,
        }

        async with aiohttp.ClientSession(
            headers=self._headers()
        ) as session:
            async with session.post(
                f"{self.BASE_URL}/answers",
                params={
                    "callback_id": callback_id,
                },
                json=body,
            ) as response:
                data = await response.json()

                if response.status != 200:
                    raise RuntimeError(
                        "Ошибка MAX callback: "
                        f"{response.status} {data}"
                    )

                return data