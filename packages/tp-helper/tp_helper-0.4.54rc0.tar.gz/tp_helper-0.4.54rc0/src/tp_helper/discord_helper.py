import inspect
import json
import traceback
from datetime import datetime, UTC
from io import BytesIO
from pathlib import Path

import aiohttp
from typing import Optional


class DiscordHelper:
    RED = 16711680
    GREEN = 5025616
    YELLOW = 16776960

    MAX_DISCORD_CONTENT = 2000
    MAX_DISCORD_EMBED_DESC = 4096
    MAX_DISCORD_EMBED_TITLE = 256
    MAX_DISCORD_FILE_SIZE = 8 * 1024 * 1024

    def __init__(self, url: str):
        self.url: str = url
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.color: Optional[int] = None
        self.notify_everyone: bool = False
        self.proxy: Optional[str] = None
        self.files = []

    def reset(self) -> "DiscordHelper":
        """Сбрасывает все параметры сообщения к значениям по умолчанию."""
        self.title = None
        self.description = None
        self.color = None
        self.notify_everyone = False
        self.files = []
        return self

    def set_proxy(self, proxy_url: str) -> "DiscordHelper":
        """
        Устанавливает прокси-сервер (HTTP, HTTPS, SOCKS5).

        # HTTP-прокси (обычный)
        discord.set_proxy("http://1.1.1.1:1080")

        # HTTPS-прокси
        discord.set_proxy("https://user:password@proxy.example.com:8080")

        # SOCKS5-прокси (например, через Tor)
        discord.set_proxy("socks5h://127.0.0.1:9050")
        """
        self.proxy = proxy_url
        return self

    def set_title(self, title: str) -> "DiscordHelper":
        """Устанавливает заголовок сообщения."""
        self.title = title
        return self

    def set_description(self, description: str) -> "DiscordHelper":
        """Устанавливает описание сообщения."""
        self.description = description
        return self

    def add_file_from_str(
        self, filename: str, content: str, encoding: str = "utf-8"
    ) -> "DiscordHelper":
        """
        Добавляет файл, созданный из строки (например, лог, CSV и т.д.)
        """

        file_bytes = content.encode(encoding)

        if len(file_bytes) > self.MAX_DISCORD_FILE_SIZE:
            truncated_notice = b"\n\n--- [truncated] ---"
            max_bytes = self.MAX_DISCORD_FILE_SIZE - len(truncated_notice) - 10
            file_bytes = file_bytes[:max_bytes].rstrip() + truncated_notice
            print(f"⚠️ Файл '{filename}' был обрезан до 8MB для отправки в Discord")

        file_obj = BytesIO(file_bytes)
        self.files.append((filename, file_obj))
        return self

    def set_color(self, color: int) -> "DiscordHelper":
        """Устанавливает цвет сообщения (в формате int)."""
        self.color = color
        return self

    def set_color_red(self) -> "DiscordHelper":
        """Устанавливает цвет сообщения на красный (ошибка)."""
        return self.set_color(self.RED)

    def set_color_green(self) -> "DiscordHelper":
        """Устанавливает цвет сообщения на зеленый (успех, информация)."""
        return self.set_color(self.GREEN)

    def set_color_yellow(self) -> "DiscordHelper":
        """Устанавливает цвет сообщения на желтый (предупреждение)."""
        return self.set_color(self.YELLOW)

    def set_notify_everyone(self) -> "DiscordHelper":
        """Определяет, следует ли упоминать @everyone в сообщении."""
        self.notify_everyone = True
        return self

    async def send_with_level(
        self, level: str, message: str = None, desc: Optional[str] = None
    ):
        """Отправляет сообщение с заданным уровнем (Error, Warning, Info)."""
        if self.title is None:
            self.set_title(f"[{level}]")
        if desc:
            self.set_description(desc)
        await self.send(message)

    async def send_error(self, message: str = None, desc: Optional[str] = None):
        """Отправляет сообщение об ошибке."""
        self.set_color_red()
        self.set_notify_everyone()
        await self.send_with_level("Error", message, desc)

    async def send_traceback_report(
        self,
        e: Exception,
        message: str = None,
        desc: str = None,
    ) -> None:
        """
        Отправляет сообщение об ошибке с автоматически сформированным заголовком вида:
        (ClassName) file_name.py
        И прикладывает traceback как файл.
        """

        if message is None:
            message = f"\n{type(e).__name__}: {str(e)}"

        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            last = tb[-1]
            filename = Path(last.filename).name
            lineno = last.lineno
        else:
            filename = "unknown.py"
            lineno = -1

        # Пытаемся найти имя класса из стека вызова
        class_name = "UnknownClass"
        for frame_info in inspect.stack():
            self_obj = frame_info.frame.f_locals.get("self")
            if self_obj and self_obj.__class__.__name__ != self.__class__.__name__:
                class_name = self_obj.__class__.__name__
                break

        self.set_title(f"({class_name}) {filename}:{lineno}")
        self.set_color_red()
        self.set_notify_everyone()

        # Формируем текст ошибки
        tb_text = "".join(
            traceback.format_exception(type(e), e, e.__traceback__)
        ).strip()

        # Прикрепляем traceback как файл
        utc_now = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"traceback_{utc_now}.log"

        self.add_file_from_str(file_name, tb_text)

        await self.send_error(message=message, desc=desc)

    async def send_warning(self, message: str = None, desc: Optional[str] = None):
        """Отправляет предупреждающее сообщение."""
        self.set_color_yellow()
        await self.send_with_level("Warning", message, desc)

    async def send_info(self, message: str = None, desc: Optional[str] = None):
        """Отправляет информационное сообщение."""
        self.set_color_green()
        await self.send_with_level("Info", message, desc)

    async def send(self, message: Optional[str] = None):
        """Отправляет сообщение с текущими параметрами."""
        if not message:
            message = ""
        await self._send_message(message)

    async def _send_message(self, content: str):
        content = f"{'@everyone ' if self.notify_everyone else ''}{content}"
        content = self._trim(content, self.MAX_DISCORD_CONTENT)

        self.title = self._trim(self.title, self.MAX_DISCORD_EMBED_TITLE)
        self.description = self._trim(self.description, self.MAX_DISCORD_EMBED_DESC)

        payload = {
            "content": content,
            "tts": False,
            "username": "🤖️",
            "embeds": [
                {
                    "title": self.title,
                    "description": self.description,
                    "color": self.color,
                }
            ],
        }

        try:
            async with aiohttp.ClientSession() as session:
                if self.files:
                    form = aiohttp.FormData()
                    form.add_field("payload_json", json.dumps(payload))

                    for idx, (filename, file_obj) in enumerate(self.files):
                        form.add_field(
                            f"file{idx}",
                            file_obj,
                            filename=filename,
                            content_type="application/octet-stream",
                        )

                    async with session.post(
                        self.url, data=form, proxy=self.proxy
                    ) as response:
                        if response.status not in (200, 204):
                            print(
                                f"Ошибка отправки в Discord: {response.status} - {await response.text()}"
                            )
                else:
                    async with session.post(
                        self.url, json=payload, proxy=self.proxy
                    ) as response:
                        if response.status != 204:
                            print(
                                f"Ошибка отправки в Discord: {response.status} - {await response.text()}"
                            )
        except Exception as e:
            print(traceback.format_exc())
            print(f"Ошибка при отправке сообщения в Discord: {e}")

        self.reset()

    @staticmethod
    def _trim(text: Optional[str], limit: int) -> Optional[str]:
        if text is None:
            return None
        suffix = "\n... [truncated]"
        if len(text) <= limit:
            return text
        return text[: limit - len(suffix)].rstrip() + suffix
