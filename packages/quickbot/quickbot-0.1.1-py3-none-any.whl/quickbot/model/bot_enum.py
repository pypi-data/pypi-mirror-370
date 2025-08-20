from aiogram.utils.i18n import I18n
from pydantic import GetCoreSchemaHandler

# from pydantic_core.core_schema import str_schema
from pydantic_core import core_schema
from sqlalchemy.types import TypeDecorator
from sqlmodel import AutoString
from typing import Any, Self, overload


class BotEnumMetaclass(type):
    def __new__(cls, name: str, bases: tuple[type], namespace: dict[str, Any]):
        all_members = {}
        if (
            bases
            and bases[0].__name__ != "BotEnum"
            and "all_members" in bases[0].__dict__
        ):
            all_members = bases[0].__dict__["all_members"]

        annotations = {}

        for key, value in namespace.items():
            if key.isupper() and not key.startswith("__") and not key.endswith("__"):
                if not isinstance(value, EnumMember):
                    value = EnumMember(value, None)

                if key in all_members.keys() and all_members[key].value != value.value:
                    raise ValueError(
                        f"Enum member {key} already exists with different value. Use same value to extend it."
                    )

                if (
                    value.value in [member.value for member in all_members.values()]
                    and key not in all_members.keys()
                ):
                    raise ValueError(f"Duplicate enum value {value[0]}")

                member = EnumMember(
                    value=value.value,
                    loc_obj=value.loc_obj,
                    parent=None,
                    name=key,
                    casting=False,
                )

                namespace[key] = member
                all_members[key] = member
                annotations[key] = type(member)

        namespace["__annotations__"] = annotations
        namespace["all_members"] = all_members

        type_ = super().__new__(cls, name, bases, namespace)

        for key, value in all_members.items():
            if not value._parent:
                value._parent = type_

        return type_


class EnumMember(object):
    @overload
    def __init__(self, value: str) -> Self: ...

    @overload
    def __init__(self, value: Self) -> Self: ...

    @overload
    def __init__(self, value: str, loc_obj: dict[str, str]) -> Self: ...

    def __init__(
        self,
        value: str = None,
        loc_obj: dict[str, str] = None,
        parent: type = None,
        name: str = None,
        casting: bool = True,
    ) -> Self:
        if not casting:
            self._parent = parent
            self._name = name
            self.value = value
            self.loc_obj = loc_obj

    @overload
    def __new__(cls: Self, *args, **kwargs) -> Self: ...

    def __new__(cls, *args, casting: bool = True, **kwargs) -> Self:
        if (cls.__name__ == "EnumMember") or not casting:
            obj = super().__new__(cls)
            kwargs["casting"] = False
            obj.__init__(*args, **kwargs)
            return obj
        if args.__len__() == 0:
            return list(cls.all_members.values())[0]
        if args.__len__() == 1 and isinstance(args[0], str):
            for key, member in cls.all_members.items():
                if member.value == args[0]:
                    return member
            return None
        elif args.__len__() == 1:
            return {member.value: member for key, member in cls.all_members.items()}[
                args[0].value
            ]
        else:
            return args[0]

    # def __get_pydantic_core_schema__(cls, *args, **kwargs):
    #     return str_schema()

    def __get__(self, instance, owner) -> Self:
        return {
            member.value: member for key, member in self._parent.all_members.items()
        }[self.value]

    def __set__(self, instance, value):
        instance.__dict__[self] = value

    def __repr__(self):
        return f"<{self._parent.__name__ if self._parent else 'EnumMember'}.{self._name}: '{self.value}'>"

    def __str__(self):
        return self.value

    def __eq__(self, other: Self | str | Any | None) -> bool:
        if other is None:
            return False
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, EnumMember):
            return self.value == other.value and (
                issubclass(self._parent, other._parent)
                or issubclass(other._parent, self._parent)
            )
        return other.__eq__(self.value)

    def __hash__(self):
        return hash(self.value)

    def __lt__(self, other: Self | str | Any | None) -> bool:
        if isinstance(other, str):
            return self.value < other
        if isinstance(other, EnumMember):
            return self.value < other.value
        return False

    def localized(self, lang: str = None) -> str:
        if self.loc_obj:
            if not lang:
                i18n = I18n.get_current()
                if i18n:
                    lang = i18n.current_locale
                else:
                    lang = list(self.loc_obj.keys())[0]

            if lang in self.loc_obj.keys():
                return self.loc_obj[lang]
            else:
                return self.loc_obj[list(self.loc_obj.keys())[0]]

        return self.value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            function=cls._validate_from_string,
            schema=core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize_to_string, return_schema=core_schema.str_schema()
            ),
        )

    @classmethod
    def _validate_from_string(cls, value: str) -> Self:
        member = cls(value)
        if member is None:
            raise ValueError(f"Invalid value for {cls.__name__}: {value}")
        return member

    @classmethod
    def _serialize_to_string(cls, value: Self) -> str:
        return value.value


class BotEnum(EnumMember, metaclass=BotEnumMetaclass):
    all_members: dict[str, EnumMember]


class EnumType(TypeDecorator):
    impl = AutoString
    cache_ok = True

    def __init__(self, enum_type):
        self._enum_type = enum_type
        super().__init__()

    def _process_param(self, value):
        if value and isinstance(value, EnumMember):
            return value.value
        return str(value)

    def process_bind_param(self, value, dialect):
        return self._process_param(value)

    def process_result_value(self, value, dialect):
        if value:
            return self._enum_type(value)
        return None

    def process_literal_param(self, value, dialect):
        return self._process_param(value)
