import asyncio
import functools
import inspect
import traceback
from typing import Callable, Any

from tp_helper import get_full_class_name


def retry_forever(
    start_message: str,
    error_message: str,
    delay: int = 10,
    backoff: float = 1.2,
    max_delay: int = 60,
    discord_every: int = 3,
):
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        @functools.wraps(func)
        async def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            # --- Собираем контекст для подстановки в сообщения
            try:
                bound = sig.bind(self, *args, **kwargs)
                bound.apply_defaults()
                context = dict(bound.arguments)
            except Exception:
                context = {"self": self}

            str_context = {}

            for k, v in context.items():
                str_context[k] = str(v)

            # --- Распаковываем self.*
            if "self" in context:
                self_obj = context["self"]
                try:
                    for attr in dir(self_obj):
                        if not attr.startswith("_"):
                            val = getattr(self_obj, attr)
                            if not callable(val):
                                str_context[attr] = str(val)
                except Exception:
                    pass

            # --- Лог старта
            try:
                self.logger.debug(start_message.format_map(str_context))
            except Exception:
                self.logger.debug(start_message)

            # --- Цикл повторов
            current_delay = delay
            retry_count = 0

            while True:
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    retry_count += 1

                    str_context_with_exception = {
                        **str_context,
                        "e": str(e),
                        "retry_count": retry_count,
                    }

                    try:
                        err_msg = error_message.format_map(str_context_with_exception)
                    except Exception:
                        err_msg = error_message

                    self.logger.error(f"❌ {err_msg}")
                    self.logger.error(f"{get_full_class_name(e)}: {str(e)}")

                    tb = traceback.extract_tb(e.__traceback__)
                    if tb:
                        last = tb[-1]
                        self.logger.error(
                            f"📍 В {last.filename}:{last.lineno} — {last.name} → {last.line}"
                        )

                    if (
                        retry_count % discord_every == 0
                        and hasattr(self, "discord")
                        and callable(
                            getattr(self.discord, "send_traceback_report", None)
                        )
                    ):
                        try:
                            await self.discord.send_traceback_report(e, err_msg)
                        except Exception as discord_error:
                            self.logger.warning(
                                f"⚠️ Ошибка при отправке в Discord: {discord_error}"
                            )

                    self.logger.info(
                        f"🔁 Повтор #{retry_count} через {current_delay:.1f} сек..."
                    )

                    await asyncio.sleep(current_delay)
                    current_delay = min(current_delay * backoff, max_delay)

        return wrapper

    return decorator
