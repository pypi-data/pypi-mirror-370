from redis.asyncio import Redis

# Для LIFO (первым пришел, последним ушел) можно оставаться с LPUSH + BRPOP.
# Для FIFO (первым пришел, первым ушел) предпочтительнее использовать RPUSH + BLPOP,


class BaseQueueRepo:
    QUEUE_NAME = ""

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.queue_name = self.QUEUE_NAME

    async def count(self) -> int:
        return await self.redis_client.llen(self.queue_name)

    async def delete(self) -> int:
        return await self.redis_client.delete(self.queue_name)
