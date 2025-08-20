from fastapi import Depends, Request
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, TYPE_CHECKING

from ..db import get_db
from ..model.descriptors import EntityDescriptor
from .depends import get_current_user

if TYPE_CHECKING:
    from ..main import QuickBot
    from ..model.user import UserBase


class ListParams(BaseModel):
    query: str = ""
    order_by: str = ""
    limit: int = 100
    offset: int = 0


async def list_entity_items(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
    params: Annotated[ListParams, Depends()],
    current_user=Depends(get_current_user),
):
    entity_descriptor: EntityDescriptor = request.app.bot_metadata.entity_descriptors[
        request.url.path.split("/")[-1]
    ]
    entity_list = await entity_descriptor.crud.list_all(
        db_session=db_session,
        user=current_user,
    )
    return entity_list


async def get_me(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
    current_user: Annotated["UserBase", Depends(get_current_user)],
):
    app: "QuickBot" = request.app
    user = await app.user_class.bot_entity_descriptor.crud.get_by_id(
        db_session=db_session,
        user=current_user,
        id=current_user.id,
    )
    return user
