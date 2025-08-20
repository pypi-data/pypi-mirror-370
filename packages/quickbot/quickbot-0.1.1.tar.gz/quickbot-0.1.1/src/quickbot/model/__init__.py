from functools import wraps
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.state import InstanceState
from typing import cast

from .bot_enum import BotEnum, EnumMember
from ..db import async_session


class EntityPermission(BotEnum):
    LIST_RLS = EnumMember("list_rls")
    READ_RLS = EnumMember("read_rls")
    CREATE_RLS = EnumMember("create_rls")
    UPDATE_RLS = EnumMember("update_rls")
    DELETE_RLS = EnumMember("delete_rls")
    LIST_ALL = EnumMember("list_all")
    READ_ALL = EnumMember("read_all")
    CREATE_ALL = EnumMember("create_all")
    UPDATE_ALL = EnumMember("update_all")
    DELETE_ALL = EnumMember("delete_all")


def session_dep(func):
    @wraps(func)
    async def wrapper(cls, *args, **kwargs):
        if "session" in kwargs and kwargs["session"]:
            return await func(cls, *args, **kwargs)

        _session = None

        state = cast(InstanceState, inspect(cls))
        if hasattr(state, "async_session"):
            _session = state.async_session

        if not _session:
            async with async_session() as session:
                kwargs["session"] = session
                return await func(cls, *args, **kwargs)
        else:
            kwargs["session"] = _session
            return await func(cls, *args, **kwargs)

    return wrapper
