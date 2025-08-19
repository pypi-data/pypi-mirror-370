from logging import Logger
from typing import Any

from tp_helper.functions import get_full_class_name


class BaseLoggingService:
    def __init__(self, logger: Logger = None):
        self.logger = logger

    def set_logger(self, logger: Logger):
        self.logger = logger

    def logging_error(self, exception: Any, message: str, retry_delay: float | None = None) -> None:
        error_type = get_full_class_name(exception)
        error_text = str(exception)

        self.logger.error(message)
        self.logger.error(f"{error_type}: {error_text}")

        if retry_delay is not None:
            self.logger.info(f"🔁 Повтор через {retry_delay:.1f} сек...")
