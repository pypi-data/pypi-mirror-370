from redis.asyncio import Redis
from tp_helper.base_queues.base_queue_repo import BaseQueueRepo

class BaseIdleQueueRepo(BaseQueueRepo):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def signal(self):
        await self.redis_client.rpush(self.QUEUE_NAME, "")

    async def wait(self, timeout: int = 0, clear: bool = True) -> str | None:
        result = await self.redis_client.blpop([self.QUEUE_NAME], timeout=timeout)
        if result is None:
            return None
        _, data = result
        if clear:
            await self.redis_client.delete(self.QUEUE_NAME)
        return str(data)
