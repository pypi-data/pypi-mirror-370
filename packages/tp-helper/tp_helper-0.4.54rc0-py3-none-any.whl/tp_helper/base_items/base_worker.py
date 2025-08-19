from logging import Logger

from tp_helper.base_items.base_discord import BaseDiscord
from tp_helper.base_items.base_logging_service import BaseLoggingService
from tp_helper.discord_helper import DiscordHelper


class BaseWorker(BaseLoggingService, BaseDiscord):
    def __init__(self, logger: Logger, discord: DiscordHelper):
        super().__init__(logger=logger)
        self.discord = discord
