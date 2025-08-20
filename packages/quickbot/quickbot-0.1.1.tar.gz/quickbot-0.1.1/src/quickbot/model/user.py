from sqlalchemy import BigInteger
from sqlmodel import Field, ARRAY

from .bot_entity import BotEntity
from .bot_enum import EnumType
from .language import LanguageBase
from .role import RoleBase

from .descriptors import EntityField
from .settings import DbSettings as DbSettings
from .fsm_storage import FSMStorage as FSMStorage
from .view_setting import ViewSetting as ViewSetting


class UserBase(BotEntity, table=False):
    __tablename__ = "user"

    id: int = EntityField(
        description="User Telegram ID",
        sm_descriptor=Field(primary_key=True, sa_type=BigInteger),
        is_visible=False,
    )

    lang: LanguageBase = Field(
        description="User language",
        sa_type=EnumType(LanguageBase),
        default_factory=lambda: LanguageBase.EN,
    )

    is_active: bool = EntityField(description="User is active", default=True)

    name: str = EntityField(description="User name")

    roles: list[RoleBase] = Field(
        description="User roles",
        sa_type=ARRAY(EnumType(RoleBase)),
        default_factory=lambda: [RoleBase.DEFAULT_USER],
    )
