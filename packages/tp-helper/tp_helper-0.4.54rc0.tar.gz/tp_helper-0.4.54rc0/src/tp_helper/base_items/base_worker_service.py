from logging import Logger

from redis.asyncio import Redis
from tp_helper.base_items.base_logging_service import BaseLoggingService


class BaseWorkerService(BaseLoggingService):
    def __init__(self, logger: Logger, redis_client: Redis = None):
        super().__init__(logger)
        self.redis_client = redis_client
