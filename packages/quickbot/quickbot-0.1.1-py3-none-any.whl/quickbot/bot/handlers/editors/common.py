from aiogram.types import Message, CallbackQuery
from decimal import Decimal
from datetime import datetime, time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickbot.main import QuickBot
from quickbot.utils.serialization import deserialize

from ....model.bot_entity import BotEntity
from ....model.bot_enum import BotEnum
from ....model.descriptors import BotContext, FieldDescriptor
from ....model.settings import Settings
from ....model.user import UserBase
from ....utils.main import get_callable_str, get_value_repr
from ..context import ContextData, CommandContext
from .boolean import bool_editor
from .date import date_picker, time_picker
from .entity import entity_picker
from .string import string_editor


async def show_editor(message: Message | CallbackQuery, **kwargs):
    field_descriptor: FieldDescriptor = kwargs["field_descriptor"]
    current_value = kwargs["current_value"]
    user: UserBase = kwargs["user"]
    callback_data: ContextData = kwargs.get("callback_data", None)
    state_data: dict = kwargs["state_data"]
    db_session = kwargs["db_session"]
    app: "QuickBot" = kwargs["app"]

    value_type = field_descriptor.type_base

    entity_data_dict: dict = state_data.get("entity_data")
    entity_data = None

    if callback_data.context == CommandContext.COMMAND_FORM:
        cmd = app.bot_commands.get(callback_data.user_command.split("&")[0])

        entity_data = (
            {
                key: await deserialize(
                    session=kwargs["db_session"],
                    type_=cmd.param_form[key].type_,
                    value=value,
                )
                for key, value in entity_data_dict.items()
            }
            if entity_data_dict and cmd.param_form
            else None
        )

    elif callback_data.context == CommandContext.ENTITY_CREATE:
        entity_data = (
            {
                key: await deserialize(
                    session=kwargs["db_session"],
                    type_=field_descriptor.entity_descriptor.fields_descriptors[
                        key
                    ].type_,
                    value=value,
                )
                for key, value in entity_data_dict.items()
            }
            if entity_data_dict
            else None
        )
    else:
        entity_id = callback_data.entity_id
        if entity_id:
            entity_data = await field_descriptor.entity_descriptor.type_.get(
                session=db_session, id=entity_id
            )

    context = BotContext(
        db_session=db_session,
        app=app,
        app_state=kwargs["app_state"],
        user=user,
        message=message,
    )

    if field_descriptor.edit_prompt:
        edit_prompt = await get_callable_str(
            callable_str=field_descriptor.edit_prompt,
            context=context,
            descriptor=field_descriptor,
            entity=entity_data,
        )
    else:
        if field_descriptor.caption:
            caption_str = await get_callable_str(
                field_descriptor.caption,
                context=context,
                descriptor=field_descriptor,
            )
        else:
            caption_str = field_descriptor.name
        if callback_data.context == CommandContext.ENTITY_EDIT:
            db_session = kwargs["db_session"]
            app = kwargs["app"]
            edit_prompt = (
                await Settings.get(
                    Settings.APP_STRINGS_FIELD_EDIT_PROMPT_TEMPLATE_P_NAME_VALUE
                )
            ).format(
                name=caption_str,
                value=await get_value_repr(
                    value=current_value,
                    field_descriptor=field_descriptor,
                    context=context,
                    locale=user.lang,
                ),
            )
        else:
            edit_prompt = (
                await Settings.get(
                    Settings.APP_STRINGS_FIELD_CREATE_PROMPT_TEMPLATE_P_NAME
                )
            ).format(name=caption_str)

    kwargs["entity_data"] = entity_data
    kwargs["edit_prompt"] = edit_prompt

    if value_type not in [int, float, Decimal, str]:
        state_data.update({"context_data": callback_data.pack()})

    if value_type is bool:
        await bool_editor(message=message, **kwargs)

    elif value_type in [int, float, Decimal, str]:
        await string_editor(message=message, **kwargs)

    elif value_type is datetime:
        await date_picker(message=message, **kwargs)

    elif value_type is time:
        await time_picker(message=message, **kwargs)

    elif issubclass(value_type, BotEntity) or issubclass(value_type, BotEnum):
        await entity_picker(message=message, **kwargs)

    else:
        raise ValueError(f"Unsupported field type: {value_type}")
