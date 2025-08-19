from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from redis.asyncio import Redis
from tp_helper.base_queues.base_queue_repo import BaseQueueRepo

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class BaseAckListQueueRepo(Generic[SchemaType], BaseQueueRepo):
    """
    Универсальный репозиторий очереди с поддержкой подтверждения (ack) для Redis.

    Хранит данные в виде JSON-строк и обеспечивает:
    - Защиту от дублирующих записей
    - Временное извлечение элемента (до ack)
    - Явное подтверждение обработки через метод ack()

    Примеры применения:
        Гарантированная доставка сообщений между сервисами.

        Обработка критичных задач, где потеря недопустима.

        Очереди с подтверждением выполнения (ack) после успешной обработки.

        Интеграция с внешними системами, где требуется надёжная доставка.

        Механизм повторной обработки задач при сбое.

        Использование в микросервисной архитектуре, где важна точная доставка и согласованность.

        Кейс "один производитель — один потребитель", когда каждая задача должна быть доставлена и подтверждена строго один раз.

    :param redis_client: Экземпляр асинхронного Redis-клиента.
    :param schema: Класс схемы Pydantic, используемой для сериализации и валидации.
    """

    def __init__(self, redis_client: Redis, schema: Type[SchemaType]):
        super().__init__(redis_client)
        self.redis_client = redis_client
        self.schema = schema

    async def add_bulk(self, messages: list[SchemaType]):
        """
        Добавляет несколько объектов в очередь разом, вычленяя уже существующие
        """
        json_items = [schema.model_dump_json() for schema in messages]
        in_queue = await self.redis_client.lrange(self.QUEUE_NAME, 0, -1)
        for message in in_queue:
            if message in json_items:
                json_items.remove(message)

        await self.redis_client.rpush(self.QUEUE_NAME, *json_items)

    async def add(self, schema: SchemaType):
        """
        Добавляет объект в очередь, если такого ещё нет (по JSON-сравнению).
        :param schema: Объект Pydantic-схемы, который будет сериализован и добавлен.
        """
        json_item = schema.model_dump_json()
        in_queue = await self.redis_client.lrange(self.QUEUE_NAME, 0, -1)
        if json_item in in_queue:
            return
        await self.redis_client.rpush(self.QUEUE_NAME, json_item)

    async def pop(self, timeout: int = 0) -> SchemaType | None:
        """
        Блокирующе извлекает первый элемент из очереди и возвращает его обратно в очередь.

        Используется совместно с ack(): pop() временно извлекает, ack() — подтверждает.

        :return: Объект схемы или None, если очередь пуста.
        """
        result = await self.redis_client.blpop([self.QUEUE_NAME], timeout=timeout)
        if result is None:
            return None
        _, raw = result
        await self.redis_client.lpush(self.QUEUE_NAME, raw)
        return self._validate(raw)

    async def ack(self):
        """
        Подтверждает получение элемента, удаляя его окончательно из очереди.

        Предполагается, что ack() вызывается после pop().
        """
        await self.redis_client.lpop(self.QUEUE_NAME)

    def _validate(self, raw: str) -> SchemaType:
        """
        Валидирует и десериализует строку JSON в объект схемы.

        Может быть переопределён в наследниках для кастомной логики.

        :param raw: JSON-строка, извлечённая из Redis.
        :return: Объект схемы.
        """
        return self.schema.model_validate_json(raw)
