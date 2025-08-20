from sqlmodel import SQLModel, Field, BigInteger
from sqlalchemy.ext.asyncio.session import AsyncSession

from . import session_dep


class ViewSetting(SQLModel, table=True):
    __tablename__ = "view_setting"
    user_id: int = Field(
        sa_type=BigInteger, primary_key=True, foreign_key="user.id", ondelete="CASCADE"
    )
    entity_name: str = Field(primary_key=True)
    filter: str | None = None

    @classmethod
    @session_dep
    async def get_filter(
        cls, *, session: AsyncSession | None = None, user_id: int, entity_name: str
    ):
        setting = await session.get(cls, (user_id, entity_name))
        return setting.filter if setting else None

    @classmethod
    @session_dep
    async def set_filter(
        cls,
        *,
        session: AsyncSession | None = None,
        user_id: int,
        entity_name: str,
        filter: str,
    ):
        setting = await session.get(cls, (user_id, entity_name))
        if setting:
            setting.filter = filter
        else:
            setting = cls(user_id=user_id, entity_name=entity_name, filter=filter)
            session.add(setting)
        await session.commit()
