import time
from datetime import timedelta
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from redis.asyncio import Redis

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class BaseStreamQueueRepo(Generic[SchemaType]):
    """
    Репозиторий для работы с Redis Stream (XADD/XREADGROUP) с использованием Consumer Group.

    Поддерживает:
    - Добавление сообщений в поток
    - Получение сообщений через группу
    - Подтверждение обработки (XACK)
    - Авто-клейм сообщений (XAUTOCLAIM) при сбоях
    """

    def __init__(self, redis_client: Redis, schema: Type[SchemaType], queue_name: str):
        self.redis_client = redis_client
        self.schema = schema
        self.queue_name = queue_name

    async def add(self, schema: SchemaType) -> None:
        """
        Добавляет элемент в поток.
        """
        data = schema.model_dump_json()
        await self.redis_client.xadd(self.queue_name, fields={"payload": data})

    async def create_consumer_group(
        self, group_name: str, stream_id: str = "0-0", create_stream: bool = True
    ) -> None:
        """
        Создаёт группу потребителей, если она ещё не существует.
        """
        try:
            await self.redis_client.xgroup_create(
                name=self.queue_name,
                groupname=group_name,
                id=stream_id,
                mkstream=create_stream,
            )
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                raise

    async def pop(
        self,
        group_name: str,
        consumer_name: str,
        stream_id: str = ">",
        block: int = 0,
        count: int = 100,
        prioritize_claimed: bool = True,
        min_idle_time: int = 60000,
    ) -> list[tuple[str, SchemaType]]:
        """
        Получает сообщения из Redis Stream.

        Если `prioritize_claimed=True`, сначала пытается забрать зависшие (XAUTOCLAIM).
        Если зависших нет — читает новые (XREADGROUP).
        """
        if prioritize_claimed:
            claimed = await BaseStreamQueueRepo.claim_reassign(
                self,
                group_name=group_name,
                consumer_name=consumer_name,
                min_idle_time=min_idle_time,
                count=count,
            )
            if claimed:
                return claimed

        result = await self.redis_client.xreadgroup(
            groupname=group_name,
            consumername=consumer_name,
            streams={self.queue_name: stream_id},
            count=count,
            block=block,
        )
        if not result:
            return []
        _, messages = result[0]

        return [
            (msg_id, self.schema.model_validate_json(data["payload"]))
            for msg_id, data in messages
        ]

    async def ack(self, group_name: str, message_id: str) -> None:
        """
        Подтверждает обработку сообщения.
        """
        await self.redis_client.xack(self.queue_name, group_name, message_id)

    async def claim_reassign(
        self,
        group_name: str,
        consumer_name: str,
        min_idle_time: int = 60000,
        count: int = 100,
    ) -> list[tuple[str, SchemaType]]:
        """
        Переназначает до `count` зависших сообщений текущему consumer'у
        с помощью XAUTOCLAIM и заново добавляет их в поток (XADD),
        чтобы они были доступны другим consumer'ам через XREADGROUP с ">".
        """
        _, messages, _ = await self.redis_client.xautoclaim(
            name=self.queue_name,
            groupname=group_name,
            consumername=consumer_name,
            min_idle_time=min_idle_time,
            start_id="0-0",
            count=count,
        )

        if not messages:
            return []

        return [
            (msg_id, self.schema.model_validate_json(data["payload"]))
            for msg_id, data in messages
        ]

    async def delete_all(self) -> None:
        """
        Полностью очищает очередь Redis Stream:
        - Удаляет сам поток
        - Удаляет все consumer group
        """
        try:
            # Удаляем все consumer group (если есть)
            groups = await self.redis_client.xinfo_groups(self.queue_name)
            for group in groups:
                group_name = group["name"]
                await self.redis_client.xgroup_destroy(self.queue_name, group_name)
        except Exception as e:
            if "no such key" not in str(e).lower():
                raise

        # Удаляем сам поток
        await self.redis_client.delete(self.queue_name)

    async def trim_by_age(self, retention: timedelta) -> int:
        """
        Удаляет сообщения старше указанного времени хранения (retention),
        используя Redis XTRIM MINID.

        :param retention: Максимальный "возраст" сообщений (например, timedelta(days=1))
        :return: Примерное количество удалённых сообщений
        """
        now_ms = int(time.time() * 1000)
        retention_ms = int(retention.total_seconds() * 1000)
        min_id = f"{now_ms - retention_ms}-0"
        return await self.redis_client.xtrim(self.queue_name, minid=min_id)
