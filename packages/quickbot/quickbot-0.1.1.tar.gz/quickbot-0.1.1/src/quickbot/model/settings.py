from types import NoneType, UnionType
from aiogram.utils.i18n.context import get_i18n
from datetime import datetime
from sqlmodel import SQLModel, Field, select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, get_args, get_origin

from ..db import async_session
from .role import RoleBase
from .descriptors import FieldDescriptor, Setting
from ..utils.serialization import deserialize, serialize

import ujson as json


class DbSettings(SQLModel, table=True):
    __tablename__ = "settings"
    name: str = Field(primary_key=True)
    value: str


class SettingsMetaclass(type):
    def __new__(cls, class_name, base_classes, attributes):
        settings_descriptors = {}

        if base_classes:
            settings_descriptors = base_classes[0].__dict__.get(
                "_settings_descriptors", {}
            )

        for annotation in attributes.get("__annotations__", {}):
            if annotation in ["_settings_descriptors", "_cache", "_cached_settings"]:
                continue

            attr_value = attributes.get(annotation)
            name = annotation

            type_ = attributes["__annotations__"][annotation]

            if isinstance(attr_value, Setting):
                descriptor_kwargs = attr_value.__dict__.copy()
                name = descriptor_kwargs.pop("name") or annotation
                attributes[annotation] = FieldDescriptor(
                    name=name,
                    field_name=annotation,
                    type_=type_,
                    type_base=type_,
                    **descriptor_kwargs,
                )

            else:
                attributes[annotation] = FieldDescriptor(
                    name=annotation,
                    field_name=annotation,
                    type_=type_,
                    type_base=type_,
                    default=attr_value,
                )

            type_origin = get_origin(type_)

            if type_origin is list:
                attributes[annotation].is_list = True
                attributes[annotation].type_base = type_ = get_args(type_)[0]

            elif type_origin == UnionType and get_args(type_)[1] == NoneType:
                attributes[annotation].is_optional = True
                attributes[annotation].type_base = type_ = get_args(type_)[0]

            settings_descriptors[name] = attributes[annotation]

            if (
                base_classes
                and base_classes[0].__name__ == "Settings"
                and hasattr(base_classes[0], annotation)
            ):
                setattr(base_classes[0], annotation, attributes[annotation])

        attributes["__annotations__"] = {}
        attributes["_settings_descriptors"] = settings_descriptors

        return super().__new__(cls, class_name, base_classes, attributes)


class Settings(metaclass=SettingsMetaclass):
    _cache: dict[str, Any] = dict[str, Any]()
    _settings_descriptors: dict[str, FieldDescriptor] = {}

    PAGE_SIZE: int = Setting(
        default=10,
    )
    SECURITY_PARAMETERS_ROLES: list[RoleBase] = Setting(
        name="SECPARAMS_ROLES", default=[RoleBase.SUPER_USER], is_visible=False
    )

    APP_STRINGS_WELCOME_P_NAME: str = Setting(
        name="AS_WELCOME", default="Welcome, {name}", is_visible=False
    )
    APP_STRINGS_GREETING_P_NAME: str = Setting(
        name="AS_GREETING", default="Hello, {name}", is_visible=False
    )
    APP_STRINGS_INTERNAL_ERROR_P_ERROR: str = Setting(
        name="AS_INTERNAL_ERROR", default="Internal error\n{error}", is_visible=False
    )
    APP_STRINGS_USER_BLOCKED_P_NAME: str = Setting(
        name="AS_USER_BLOCKED", default="User {name} is blocked", is_visible=False
    )
    APP_STRINGS_FORBIDDEN: str = Setting(
        name="AS_FORBIDDEN", default="Forbidden", is_visible=False
    )
    APP_STRINGS_NOT_FOUND: str = Setting(
        name="AS_NOT_FOUND", default="Object not found", is_visible=False
    )
    APP_STRINGS_MAIN_NENU: str = Setting(
        name="AS_MAIN_MENU", default="Main menu", is_visible=False
    )
    APP_STRINGS_REFERENCES: str = Setting(
        name="AS_REFERENCES", default="References", is_visible=False
    )
    APP_STRINGS_REFERENCES_BTN: str = Setting(
        name="AS_REFERENCES_BTN", default="📚 References", is_visible=False
    )
    APP_STRINGS_SETTINGS: str = Setting(
        name="AS_SETTINGS", default="Settings", is_visible=False
    )
    APP_STRINGS_SETTINGS_BTN: str = Setting(
        name="AS_SETTINGS_BTN", default="⚙️ Settings", is_visible=False
    )
    APP_STRINGS_PARAMETERS: str = Setting(
        name="AS_PARAMETERS", default="Parameters", is_visible=False
    )
    APP_STRINGS_PARAMETERS_BTN: str = Setting(
        name="AS_PARAMETERS_BTN", default="🎛️ Parameters", is_visible=False
    )
    APP_STRINGS_LANGUAGE: str = Setting(
        name="AS_LANGUAGE", default="Language", is_visible=False
    )
    APP_STRINGS_LANGUAGE_BTN: str = Setting(
        name="AS_LANGUAGE_BTN", default="🗣️ Language", is_visible=False
    )
    APP_STRINGS_BACK_BTN: str = Setting(
        name="AS_BACK_BTN", default="⬅️ Back", is_visible=False
    )
    APP_STRINGS_DELETE_BTN: str = Setting(
        name="AS_DELETE_BTN", default="🗑️ Delete", is_visible=False
    )
    APP_STRINGS_CONFIRM_DELETE_P_NAME: str = Setting(
        name="AS_CONFIRM_DEL",
        default='Are you sure you want to delete "{name}"?',
        is_visible=False,
    )
    APP_STRINGS_EDIT_BTN: str = Setting(
        name="AS_EDIT_BTN", default="✏️ Edit", is_visible=False
    )
    APP_STRINGS_ADD_BTN: str = Setting(
        name="AS_ADD_BTN", default="➕ Add", is_visible=False
    )
    APP_STRINGS_YES_BTN: str = Setting(
        name="AS_YES_BTN", default="✅ Yes", is_visible=False
    )
    APP_STRINGS_NO_BTN: str = Setting(
        name="AS_NO_BTN", default="❌ No", is_visible=False
    )
    APP_STRINGS_CANCEL_BTN: str = Setting(
        name="AS_CANCEL_BTN", default="❌ Cancel", is_visible=False
    )
    APP_STRINGS_CLEAR_BTN: str = Setting(
        name="AS_CLEAR_BTN", default="⌫ Clear", is_visible=False
    )
    APP_STRINGS_DONE_BTN: str = Setting(
        name="AS_DONE_BTN", default="✅ Done", is_visible=False
    )
    APP_STRINGS_SKIP_BTN: str = Setting(
        name="AS_SKIP_BTN", default="⏩️ Skip", is_visible=False
    )
    APP_STRINGS_FIELD_EDIT_PROMPT_TEMPLATE_P_NAME_VALUE: str = Setting(
        name="AS_FIELDEDIT_PROMPT",
        default='Enter new value for "{name}" (current value: {value})',
        is_visible=False,
    )
    APP_STRINGS_FIELD_CREATE_PROMPT_TEMPLATE_P_NAME: str = Setting(
        name="AS_FIELDCREATE_PROMPT",
        default='Enter new value for "{name}"',
        is_visible=False,
    )
    APP_STRINGS_STRING_EDITOR_LOCALE_TEMPLATE_P_NAME: str = Setting(
        name="AS_STREDIT_LOC_TEMPLATE", default='string for "{name}"', is_visible=False
    )
    APP_STRINGS_VIEW_FILTER_EDIT_PROMPT: str = Setting(
        name="AS_FILTEREDIT_PROMPT", default="Enter filter value", is_visible=False
    )
    APP_STRINGS_INVALID_INPUT: str = Setting(
        name="AS_INVALID_INPUT", default="Invalid input", is_visible=False
    )

    @classmethod
    async def get[T](
        cls,
        param: T,
        session: AsyncSession = None,
        all_locales=False,
        locale: str = None,
    ) -> T:
        name = param.field_name

        if name not in cls._cache.keys():
            if session is None:
                async with async_session() as session:
                    cls._cache[name] = await cls.load_param(
                        session=session, param=param
                    )
            else:
                cls._cache[name] = await cls.load_param(session=session, param=param)

        ret_val = cls._cache[name]

        if param.localizable and not all_locales:
            if not locale:
                locale = get_i18n().current_locale
            try:
                obj = json.loads(ret_val)
            except Exception:
                return ret_val
            return obj.get(locale, obj[list(obj.keys())[0]])

        return ret_val

    @classmethod
    async def load_param(cls, session: AsyncSession, param: FieldDescriptor) -> Any:
        db_setting = (
            await session.exec(
                select(DbSettings).where(DbSettings.name == param.field_name)
            )
        ).first()

        if db_setting:
            return await deserialize(
                session=session, type_=param.type_, value=db_setting.value
            )

        return (
            param.default_factory()
            if param.default_factory
            else param.default
            if param.default
            else (
                []
                if (get_origin(param.type_) is list or param.type_ is list)
                else datetime(2000, 1, 1)
                if param.type_ == datetime
                else param.type_()
            )
        )

    # @classmethod
    # async def load_params(cls):
    #     async with async_session() as session:
    #         db_settings = (await session.exec(select(DbSettings))).all()
    #         for db_setting in db_settings:
    #             if db_setting.name in cls.__dict__:
    #                 setting = cls.__dict__[db_setting.name]  # type: FieldDescriptor
    #                 cls._cache[db_setting.name] = await deserialize(
    #                     session=session,
    #                     type_=setting.type_,
    #                     value=db_setting.value,
    #                 )

    #     cls._loaded = True

    @classmethod
    async def set_param(cls, param: str | FieldDescriptor, value) -> None:
        if isinstance(param, str):
            param = cls._settings_descriptors[param]
        ser_value = serialize(value, param)
        async with async_session() as session:
            db_setting = (
                await session.exec(
                    select(DbSettings).where(DbSettings.name == param.field_name)
                )
            ).first()
            if db_setting is None:
                db_setting = DbSettings(name=param.field_name)
            db_setting.value = str(ser_value)
            session.add(db_setting)
            await session.commit()
        cls._cache[param.field_name] = value

    @classmethod
    def list_params(cls) -> dict[str, FieldDescriptor]:
        return cls._settings_descriptors

    @classmethod
    async def get_params(cls) -> dict[FieldDescriptor, Any]:
        params = cls.list_params()
        return {
            param: await cls.get(param, all_locales=True) for _, param in params.items()
        }
