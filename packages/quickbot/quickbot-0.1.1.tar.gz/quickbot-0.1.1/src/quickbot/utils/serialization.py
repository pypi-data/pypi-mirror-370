from datetime import datetime, time
from decimal import Decimal
from sqlmodel import select, column
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, Union, get_origin, get_args
from types import UnionType, NoneType
import ujson as json

from quickbot.model.descriptors import FieldDescriptor


async def deserialize[T](session: AsyncSession, type_: type[T], value: str = None) -> T:
    type_origin = get_origin(type_)
    is_optional = False
    if type_origin in [UnionType, Union]:
        args = get_args(type_)
        if args[1] is NoneType:
            type_ = args[0]
            if value is None:
                return None
            is_optional = True
    if get_origin(type_) is list:
        arg_type = None
        args = get_args(type_)
        if args:
            arg_type = args[0]
        values = json.loads(value) if value else []
        if arg_type:
            if hasattr(arg_type, "bot_entity_descriptor"):
                ret = list[arg_type]()
                items = (
                    await session.exec(select(arg_type).where(column("id").in_(values)))
                ).all()
                for item in items:
                    ret.append(item)
                return ret
            elif hasattr(arg_type, "all_members"):
                return [arg_type(value) for value in values]
            else:
                return [arg_type(value) for value in values]
        else:
            return values
    elif hasattr(type_, "bot_entity_descriptor"):
        if is_optional and not value:
            return None
        return await session.get(type_, int(value))
    elif hasattr(type_, "all_members"):
        if is_optional and not value:
            return None
        return type_(value)
    elif type_ is time:
        if is_optional and not value:
            return None
        return time.fromisoformat(value.replace("-", ":"))
    elif type_ is datetime:
        if is_optional and not value:
            return None
        if value[-3] == "-":
            return datetime.strptime(value, "%Y-%m-%d %H-%M")
        else:
            return datetime.fromisoformat(value)
    elif type_ is bool:
        return value == "True"
    elif type_ is Decimal:
        if is_optional and not value:
            return None
        return Decimal(value)

    if is_optional and not value:
        return None
    return type_(value)


def serialize(value: Any, field_descriptor: FieldDescriptor) -> str:
    if value is None:
        return ""
    type_ = field_descriptor.type_base

    if field_descriptor.is_list:
        if hasattr(type_, "bot_entity_descriptor"):
            return json.dumps([item.id for item in value], ensure_ascii=False)
        elif hasattr(type_, "all_members"):
            return json.dumps([item.value for item in value], ensure_ascii=False)
        else:
            return json.dumps(value, ensure_ascii=False)
    elif hasattr(type_, "bot_entity_descriptor"):
        return str(value.id) if value else ""
    return str(value)
