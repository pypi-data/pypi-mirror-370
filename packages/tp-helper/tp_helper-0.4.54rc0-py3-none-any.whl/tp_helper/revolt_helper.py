import logging
import aiohttp


class RevoltHelper:
    def __init__(self, url, token, channel_id):
        self.message_url = f"{url}/channels/{channel_id}/messages"
        self.token = token
        self.title = None
        self.description = None
        self.colour = None

    def set_title(self, title):
        self.title = title

    def set_description(self, description):
        self.description = description

    def set_colour(self, colour):
        self.colour = colour

    async def send_error(self, error, desc: str = None):
        self.title = "[Error]"
        self.description = desc
        self.colour = "#ff0000"
        await self._send_message(f"```{error}```")

    async def send_warning(self, warning, desc: str = None):
        self.title = "[Warning]"
        self.description = desc
        self.colour = "#ff8800"
        await self._send_message(f"```{warning}```")

    async def send_info(self, info, desc: str = None):
        self.title = "[Info]"
        self.description = desc
        self.colour = "#00ff00"
        await self._send_message(f"```{info}```")

    async def _send_message(self, message: str):
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    self.message_url,
                    json={
                        "content": message,
                        "embeds": [
                            {
                                "title": self.title,
                                "description": self.description,
                                "colour": self.colour,
                            }
                        ],
                    },
                    headers={
                        "X-Bot-Token": self.token,
                        "Content-Type": "application/json",
                    },
                )
                if response.status != 200:
                    logging.warn(
                        f"Non-200 response from Revolt! Response: {await response.text()}"
                    )
        except Exception as e:
            logging.error(f"Could not send message to Revolt: {e}")
