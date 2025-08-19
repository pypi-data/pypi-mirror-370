from redis.asyncio import Redis
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from tp_helper.base_queues.base_queue_repo import BaseQueueRepo

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class BaseFastQueueRepo(Generic[SchemaType], BaseQueueRepo):
    """
    Универсальный репозиторий Redis-очереди для быстрой обработки элементов БЕЗ подтверждения (ack).

    Подходит для ситуаций, когда:
    - Элемент должен быть немедленно обработан и удалён (fire-and-forget)
    - Повторная обработка допустима в случае сбоя

    Использует Pydantic-схемы для сериализации и валидации данных.

    :param redis_client: Асинхронный Redis-клиент.
    :param schema: Класс схемы (наследник Pydantic BaseModel) для сериализации и валидации.

    Примеры применения:
        Очередь задач для параллельных обработчиков (воркеров).

        Простое распределение заданий между несколькими обработчиками.

        Высокопроизводительные системы с допустимой потерей части задач при сбое.

        Запуск задач в real-time без необходимости подтверждения обработки.

        Подпитка воркеров из внешних сервисов (например, при обработке webhook-ов или событий).

        Быстрая доставка сообщений без повторных попыток и резервного хранения.
    """

    def __init__(self, redis_client: Redis, schema: Type[SchemaType]):
        super().__init__(redis_client)
        self.redis_client = redis_client
        self.schema = schema

    async def pop(self, timeout: int = 0) -> SchemaType | None:
        """
        Блокирующе извлекает и удаляет первый элемент из очереди (BLPOP).

        :param timeout: Таймаут ожидания в секундах. Если 0 — ждет бесконечно.
        :return: Объект схемы или None, если таймаут истёк.
        """
        result = await self.redis_client.blpop([self.queue_name], timeout=timeout)
        if result is None:
            return None
        _, raw = result
        return self._validate(raw) if raw else None

    async def add(self, schema: SchemaType):
        """
        Добавляет объект в очередь, если он ещё не присутствует (по JSON-сравнению).

        :param schema: Объект схемы для добавления.
        """
        json_item = schema.model_dump_json()
        in_queue = await self.redis_client.lrange(self.queue_name, 0, -1)
        if json_item in in_queue:
            return
        await self.redis_client.rpush(self.queue_name, json_item)

    def _validate(self, raw: str) -> SchemaType:
        """
        Преобразует JSON-строку в объект схемы.

        Может быть переопределён в наследниках для дополнительной логики валидации.

        :param raw: JSON-строка, извлечённая из Redis.
        :return: Объект схемы.
        """
        return self.schema.model_validate_json(raw)
