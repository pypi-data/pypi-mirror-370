from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_session(self):
        return self.session
