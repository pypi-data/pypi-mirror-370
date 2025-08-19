from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import (
    Delete,
    Select,
    Update,
    and_,
    delete,
    select,
    update, Enum,
)
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute
from tp_helper.base_queues.base_repo import BaseRepo

from tp_helper.types.null_filter_type import NullFilterType

ModelSchema = TypeVar("ModelSchema", bound=DeclarativeBase)
FilterSchema = TypeVar("FilterSchema", bound=BaseModel)


class BaseDBRepo(BaseRepo, Generic[ModelSchema, FilterSchema]):
    """
    Универсальный асинхронный репозиторий для SQLAlchemy-моделей с фильтрацией через Pydantic-схемы.

    Позволяет выполнять CRUD-операции (create, find, update, delete),
    автоматически обрабатывая фильтры, сортировку, пагинацию и диапазоны значений (`*_from`, `*_to`, `*_ids`).

    Пример использования:
    ```python
    repo = BaseDBRepo(UserModel, UserFilterSchema, session)
    await repo.find(UserFilterSchema(email="test@example.com", created_at_from=datetime(...)))
    ```
    """

    def __init__(
        self,
        model: type[ModelSchema],
        filter_schema: type[FilterSchema],
        session: AsyncSession,
    ):
        """
        Инициализация универсального репозитория.

        :param model: SQLAlchemy модель
        :param filter_schema: Pydantic-схема фильтрации
        :param session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session)
        self.model = model
        self.filter_schema = filter_schema

    def build_stmt(
        self,
        stmt: Select | Update | Delete,
        f: FilterSchema,
    ) -> Select | Update | Delete:
        """
        Строит SQL-запрос с учетом фильтрации, сортировки и пагинации на основе схемы фильтра.

        Поддержка:
        - `*_from`, `*_to` — фильтрация по диапазону
        - `*_ids` — фильтрация по списку значений
        - `sort_field`, `sort_order`, `limit`, `offset`

        :param stmt: Базовый SQL-выражение (Select, Update, Delete)
        :param f: Экземпляр схемы фильтрации
        :return: Обновленное выражение с условиями
        """
        filters = []

        for name, value in f.model_dump(exclude_none=True).items():
            if name in {"sort_field", "sort_order", "limit", "offset"}:
                continue

            column = getattr(self.model, name, None)

            if isinstance(value, NullFilterType) and isinstance(column, InstrumentedAttribute):
                if value == NullFilterType.IS_NULL:
                    filters.append(column.is_(None))
                elif value == NullFilterType.IS_NOT_NULL:
                    filters.append(column.isnot(None))
                continue

            if name.endswith("_from"):
                field = name[:-5]
                column = getattr(self.model, field, None)
                if isinstance(column, InstrumentedAttribute):
                    filters.append(column >= value)

            elif name.endswith("_to"):
                field = name[:-3]
                column = getattr(self.model, field, None)
                if isinstance(column, InstrumentedAttribute):
                    filters.append(column <= value)

            elif name.endswith("s") and isinstance(value, list):
                field = name[:-1]
                column = getattr(self.model, field, None)
                if isinstance(column, InstrumentedAttribute):
                    filters.append(column.in_(value))

            else:
                column = getattr(self.model, name, None)
                if isinstance(column, InstrumentedAttribute):
                    filters.append(column == value)

        if filters:
            stmt = stmt.where(and_(*filters))

        if isinstance(stmt, Select):
            sort_field = getattr(f, "sort_field", None)
            if sort_field:
                sort_attr = (
                    sort_field.value
                    if isinstance(sort_field, Enum)
                    else str(sort_field)
                )
                sort_column = getattr(self.model, sort_attr, None)
                if isinstance(sort_column, InstrumentedAttribute):
                    if getattr(f, "sort_order", None) == "desc":
                        sort_column = sort_column.desc()
                    stmt = stmt.order_by(sort_column)

            if getattr(f, "limit", None) is not None:
                stmt = stmt.limit(f.limit)
            if getattr(f, "offset", None) is not None:
                stmt = stmt.offset(f.offset)

        return stmt

    def _create(
        self,
        item: ModelSchema | None = None,
        items: list[ModelSchema] | None = None,
    ):
        """
        Добавляет одну или несколько сущностей в сессию (без коммита).

        :param item: Одна модель
        :param items: Список моделей
        :return: Добавленные объекты
        """
        if item:
            self.session.add(item)
            return item
        if items:
            self.session.add_all(items)
            return items

    def create(self, item: ModelSchema) -> ModelSchema:
        """Создание одной сущности."""
        return self._create(item=item)

    def create_bulk(self, items: list[ModelSchema]) -> list[ModelSchema]:
        """Массовое создание сущностей."""
        return self._create(items=items)

    async def find_one(self, f: FilterSchema) -> ModelSchema | None:
        """
        Поиск одной сущности по фильтру.

        :param f: Схема фильтрации
        :return: Найденная сущность или None
        """
        f_copy = f.model_copy()
        f_copy.limit = 1
        result = await self.find(f_copy)
        return result.first()

    async def find(self, f: FilterSchema) -> ScalarResult[ModelSchema]:
        """
        Поиск списка сущностей по фильтру.

        :param f: Схема фильтрации
        :return: ScalarResult с результатами
        """
        stmt = self.build_stmt(select(self.model), f)
        result = await self.session.scalars(stmt)
        return result

    async def update(
        self,
        f: FilterSchema,
        values: dict[str, Any],
    ) -> None:
        """
        Обновление сущностей по фильтру.

        :param f: Схема фильтрации
        :param values: Обновляемые поля
        """
        stmt = self.build_stmt(update(self.model).values(**values), f)
        await self.session.execute(stmt)


    async def delete(self, f: FilterSchema) -> None:
        """
        Удаление сущностей по фильтру.

        :param f: Схема фильтрации
        """
        stmt = self.build_stmt(delete(self.model), f)
        await self.session.execute(stmt)
