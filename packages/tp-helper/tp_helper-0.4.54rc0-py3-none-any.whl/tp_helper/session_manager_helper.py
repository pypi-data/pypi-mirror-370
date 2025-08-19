from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
    AsyncEngine,
)
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Optional, Dict
import json


class SessionManagerHelper:
    """
    Класс-обёртка для управления асинхронными сессиями SQLAlchemy.
    """

    def __init__(
        self,
        url: str,
        scopefunc: Optional[Callable[[], Any]] = None,
        echo: bool = False,  # Логирование SQL-запросов
        pool_size: int = 5,  # Размер пула соединений
        max_overflow: int = 10,  # Максимальное количество соединений сверх pool_size
        pool_timeout: int = 30,  # Таймаут ожидания свободного соединения
        pool_recycle: int = 1800,  # Закрытие соединений после указанного времени (в секундах)
        pool_pre_ping: int = True,  # Проверка соединений перед использованием
        connect_args={},  # Дополнительные аргументы подключения
        future: bool = True,  # Включение поддержки API SQLAlchemy 2.0
        #
        autocommit=False,  # Если True, сессия автоматически выполняет COMMIT после каждого запроса.
        autoflush=False,  # Если True, изменения автоматически сбрасываются в базу перед выполнением запроса.
        # Если True, объекты становятся недействительными после коммита (по умолчанию True).
        # Если True, объекты становятся "протухшими" после коммита, что требует повторного запроса в базу.
        # Рекомендуется False для асинхронного использования.
        expire_on_commit=False,
    ) -> None:
        self.url: str = url
        self.scope_func: Optional[Callable[[], Any]] = scopefunc

        self.engine: AsyncEngine = create_async_engine(
            url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            connect_args=connect_args,
            future=future,
            json_serializer=lambda x: json.dumps(
                x, ensure_ascii=False
            ),  # Отключаем escape-последовательности
            json_deserializer=lambda x: json.loads(x),
        )

        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autocommit=autocommit,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
        )

        self._scoped_session: Optional[
            async_scoped_session[async_sessionmaker[AsyncSession]]
        ] = (
            async_scoped_session(self.session_factory, scopefunc=self.scope_func)
            if self.scope_func
            else None
        )

    @property
    def scoped_session(self) -> async_scoped_session[async_sessionmaker[AsyncSession]]:
        """Возвращает scoped-сессию, если она была инициализирована."""
        if self._scoped_session is None:
            raise RuntimeError(
                "Scoped session не инициализирован, т.к. scopefunc не был передан."
            )
        return self._scoped_session

    @asynccontextmanager
    async def _get_session(
        self, use_scoped: bool = False
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        Унифицированный контекстный менеджер для получения сессии.
        :param use_scoped: Использовать scoped session.
        """
        session_factory = self.scoped_session if use_scoped else self.session_factory
        async with session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение стандартной сессии."""
        async with self._get_session() as session:
            yield session

    @asynccontextmanager
    async def get_scoped_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение scoped-сессии."""
        async with self._get_session(use_scoped=True) as session:
            yield session

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение асинхронной сессии с обработкой ошибок."""
        async with self._get_session() as session:
            yield session
