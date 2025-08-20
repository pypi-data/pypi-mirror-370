from babel.support import LazyProxy
from inspect import iscoroutinefunction, signature
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import I18n
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, TYPE_CHECKING, Callable
import ujson as json

from quickbot.utils.serialization import deserialize
from quickbot.model.permissions import (
    _extract_rls_filter_fields,
    get_user_permissions,
    _extract_filter_fields,
)
from ..model.settings import Settings


from ..model.descriptors import (
    BotContext,
    EntityList,
    FieldDescriptor,
    EntityDescriptor,
    EntityPermission,
    _BaseFieldDescriptor,
    _BaseEntityDescriptor,
    Filter,
)

from ..bot.handlers.context import CallbackCommand, ContextData, CommandContext

if TYPE_CHECKING:
    from ..model.bot_entity import BotEntity
    from ..model.user import UserBase
    from ..main import QuickBot


def get_local_text(text: str, locale: str = None) -> str:
    if not locale:
        i18n = I18n.get_current(no_error=True)
        if i18n:
            locale = i18n.current_locale
        else:
            locale = "en"
    try:
        obj = json.loads(text)  # @IgnoreException
    except Exception:
        return text
    else:
        return obj.get(locale, obj[list(obj.keys())[0]])


def get_send_message(message: Message | CallbackQuery):
    if isinstance(message, Message):
        return message.answer
    else:
        return message.message.edit_text


def clear_state(state_data: dict, clear_nav: bool = False):
    if clear_nav:
        state_data.clear()
    else:
        stack = state_data.get("navigation_stack")
        context = state_data.get("navigation_context")
        state_data.clear()
        if stack:
            state_data["navigation_stack"] = stack
        if context:
            state_data["navigation_context"] = context


async def get_entity_item_repr(
    entity: "BotEntity",
    context: BotContext,
    item_repr: Callable[["BotEntity", BotContext], str] | None = None,
) -> str:
    descr = entity.bot_entity_descriptor

    if not item_repr:
        item_repr = descr.item_repr

    if item_repr:
        if iscoroutinefunction(item_repr):
            return await item_repr(entity, context)
        else:
            return item_repr(entity, context)

    return f"{
        await get_callable_str(
            callable_str=descr.full_name,
            context=context,
            descriptor=descr,
            entity=entity,
        )
        if descr.full_name
        else descr.name
    }: {str(entity.id)}"


async def get_value_repr(
    value: Any,
    field_descriptor: FieldDescriptor,
    context: BotContext,
    locale: str | None = None,
) -> str:
    if value is None:
        return ""

    type_ = field_descriptor.type_base
    if isinstance(value, bool):
        return "[✓]" if value else "[ ]"
    elif field_descriptor.is_list:
        if hasattr(type_, "bot_entity_descriptor"):
            return f"[{
                ', '.join(
                    [
                        await get_entity_item_repr(entity=item, context=context)
                        for item in value
                    ]
                )
            }]"
        elif hasattr(type_, "all_members"):
            return f"[{', '.join(item.localized(locale) for item in value)}]"
        elif type_ is str:
            return f"[{', '.join([f'"{item}"' for item in value])}]"
        else:
            return f"[{', '.join([str(item) for item in value])}]"
    elif hasattr(type_, "bot_entity_descriptor"):
        return await get_entity_item_repr(entity=value, context=context)
    elif hasattr(type_, "all_members"):
        return value.localized(locale)
    elif isinstance(value, str):
        if field_descriptor and field_descriptor.localizable:
            return get_local_text(text=value, locale=locale)
        return value
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return str(value)
    else:
        return str(value)


async def get_callable_str(
    callable_str: (
        str
        | LazyProxy
        | Callable[[EntityDescriptor, BotContext], str]
        | Callable[["BotEntity", BotContext], str]
        | Callable[[FieldDescriptor, "BotEntity", BotContext], str]
    ),
    context: BotContext,
    descriptor: FieldDescriptor | EntityDescriptor | None = None,
    entity: "BotEntity | Any" = None,
) -> str:
    if isinstance(callable_str, str):
        return callable_str
    elif isinstance(callable_str, LazyProxy):
        return callable_str.value
    elif callable(callable_str):
        args = signature(callable_str).parameters
        if iscoroutinefunction(callable_str):
            if len(args) == 3:
                return await callable_str(descriptor, entity, context)
            else:
                param = args[next(iter(args))]
                if not isinstance(param.annotation, str) and (
                    issubclass(param.annotation, _BaseFieldDescriptor)
                    or issubclass(param.annotation, _BaseEntityDescriptor)
                ):
                    return await callable_str(descriptor, context)
                else:
                    return await callable_str(entity, context)
        else:
            if len(args) == 3:
                return callable_str(descriptor, entity, context)
            else:
                return callable_str(entity or descriptor, context)


def get_entity_descriptor(
    app: "QuickBot", callback_data: ContextData
) -> EntityDescriptor:
    if callback_data.entity_name:
        return app.bot_metadata.entity_descriptors[callback_data.entity_name]
    return None


def get_field_descriptor(
    app: "QuickBot", callback_data: ContextData
) -> FieldDescriptor | None:
    if callback_data.context == CommandContext.SETTING_EDIT:
        return Settings.list_params()[callback_data.field_name]
    elif callback_data.context == CommandContext.COMMAND_FORM:
        command = app.bot_commands[callback_data.user_command.split("&")[0]]
        if (
            command
            and command.param_form
            and callback_data.field_name in command.param_form
        ):
            return command.param_form[callback_data.field_name]
    elif callback_data.context in [
        CommandContext.ENTITY_CREATE,
        CommandContext.ENTITY_EDIT,
        CommandContext.ENTITY_FIELD_EDIT,
    ]:
        entity_descriptor = get_entity_descriptor(app, callback_data)
        if entity_descriptor:
            return entity_descriptor.fields_descriptors.get(callback_data.field_name)
    return None


async def build_field_sequence(
    entity_descriptor: EntityDescriptor,
    user: "UserBase",
    callback_data: ContextData,
    state_data: dict,
    context: BotContext,
):
    prev_form_list = None

    stack = state_data.get("navigation_stack", [])
    prev_callback_data = ContextData.unpack(stack[-1]) if stack else None
    if (
        prev_callback_data
        and prev_callback_data.command == CallbackCommand.ENTITY_LIST
        and prev_callback_data.entity_name == entity_descriptor.name
    ):
        prev_form_name = (
            prev_callback_data.form_params.split("&")[0]
            if prev_callback_data.form_params
            else None
        )
        prev_form_list: EntityList = entity_descriptor.lists.get(
            prev_form_name, entity_descriptor.default_list
        )

    entity_data = state_data.get("entity_data", {})

    field_sequence = list[str]()
    # exclude RLS fields from edit if user has no CREATE_ALL/UPDATE_ALL permission
    user_permissions = get_user_permissions(user, entity_descriptor)
    for fd in entity_descriptor.fields_descriptors.values():
        if isinstance(fd.is_visible_in_edit_form, bool):
            skip = not fd.is_visible_in_edit_form
        elif callable(fd.is_visible_in_edit_form):
            if iscoroutinefunction(fd.is_visible_in_edit_form):
                skip = not await fd.is_visible_in_edit_form(fd, entity_data, context)
            else:
                skip = not fd.is_visible_in_edit_form(fd, entity_data, context)
        else:
            skip = False
            if (
                fd.is_optional
                or fd.field_name == "id"
                or (
                    fd.field_name[-3:] == "_id"
                    and fd.field_name[:-3] in entity_descriptor.fields_descriptors
                )
                or fd.default is not None
                or fd.default_factory is not None
            ):
                skip = True
            # Check RLS filters for field visibility
            if entity_descriptor.rls_filters:
                # Get RLS filter fields that should be auto-filled and hidden from user
                rls_filter_fields = _extract_rls_filter_fields(entity_descriptor)
                if fd.field_name in rls_filter_fields and (
                    (
                        EntityPermission.CREATE_ALL not in user_permissions
                        and callback_data.context == CommandContext.ENTITY_CREATE
                    )
                    or (
                        EntityPermission.UPDATE_ALL not in user_permissions
                        and callback_data.context == CommandContext.ENTITY_EDIT
                    )
                ):
                    skip = True

            if prev_form_list and prev_form_list.static_filters:
                static_filter_fields = _extract_filter_fields(
                    prev_form_list.static_filters, entity_descriptor.type_
                )
                if fd.field_name.rstrip("_id") in [
                    f.rstrip("_id") for f in static_filter_fields
                ]:
                    skip = True

        if not skip:
            field_sequence.append(fd.field_name)

    return field_sequence


async def prepare_static_filter(
    db_session: AsyncSession,
    entity_descriptor: EntityDescriptor,
    static_filters: list[Filter],
    params: list[str],
) -> list[Filter]:
    return (
        [
            Filter(
                field_name=f.field_name,
                operator=f.operator,
                value_type="const",
                value=(
                    f.value
                    if f.value_type == "const"
                    else await deserialize(
                        session=db_session,
                        type_=entity_descriptor.fields_descriptors[
                            f.field_name
                        ].type_base,
                        value=params[f.param_index],
                    )
                ),
            )
            for f in static_filters
        ]
        if static_filters
        else None
    )
