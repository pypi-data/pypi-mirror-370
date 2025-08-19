from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryManagerHelper:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_session(self):
        return self.session

    def close_session(self):
        return self.session

    async def __aenter__(self):
        pass

    async def session_close(self):
        await self.session.close()
