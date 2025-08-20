from inspect import iscoroutinefunction
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm.collections import InstrumentedList
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import TYPE_CHECKING, Any
from decimal import Decimal
import json

from ..context import ContextData, CallbackCommand, CommandContext
from ...command_context_filter import CallbackCommandFilter
from ..user_handlers.main import command_handler
from ....model import EntityPermission
from ....model.user import UserBase
from ....model.settings import Settings
from ....model.descriptors import (
    BotContext,
    EntityForm,
    EntityList,
    FieldDescriptor,
    Filter,
    FilterExpression,
)
from ....model.language import LanguageBase
from ....auth import authorize_command
from ....model.permissions import check_entity_permission
from ....utils.main import (
    get_user_permissions,
    clear_state,
    get_entity_descriptor,
    get_field_descriptor,
    build_field_sequence,
)
from ....utils.serialization import deserialize
from ..common.routing import route_callback
from .common import show_editor

if TYPE_CHECKING:
    from ....main import QuickBot

router = Router()


async def _validate_value(
    field_descriptor: FieldDescriptor,
    value: Any,
    message: Message | CallbackQuery,
    **kwargs: Any,
) -> bool | str:
    if field_descriptor.validator:
        context = BotContext(
            db_session=kwargs["db_session"],
            app=kwargs["app"],
            app_state=kwargs["app_state"],
            user=kwargs["user"],
            message=message,
        )
        if iscoroutinefunction(field_descriptor.validator):
            return await field_descriptor.validator(value, context)
        else:
            return field_descriptor.validator(value, context)
    return True


@router.message(CallbackCommandFilter(CallbackCommand.FIELD_EDITOR_CALLBACK))
@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.FIELD_EDITOR_CALLBACK)
)
async def field_editor_callback(message: Message | CallbackQuery, **kwargs):
    app: "QuickBot" = kwargs["app"]
    callback_data: ContextData = kwargs.get("callback_data", None)

    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    if isinstance(message, Message):
        context_data = state_data.get("context_data")
        if context_data:
            callback_data = ContextData.unpack(context_data)

        field_descriptor = get_field_descriptor(app, callback_data)

        if not field_descriptor.options_custom_value:
            return

        value = message.text
        type_base = field_descriptor.type_base

        if type_base in [int, float, Decimal]:
            try:
                val = type_base(value)  # @IgnoreException
            except Exception:
                return await message.answer(
                    text=(await Settings.get(Settings.APP_STRINGS_INVALID_INPUT))
                )
        elif type_base is str and field_descriptor.localizable:
            locale_index = int(state_data.get("locale_index"))
            val = {
                list(LanguageBase.all_members.values())[
                    locale_index
                ].value: message.text
            }
        else:
            val = value

        validation_result = await _validate_value(
            field_descriptor=field_descriptor,
            value=val,
            message=message,
            **kwargs,
        )

        if isinstance(validation_result, str):
            return await message.answer(
                text=f"{await Settings.get(Settings.APP_STRINGS_INVALID_INPUT)}\n{validation_result}"
            )
        elif not validation_result:
            return await message.answer(
                text=(await Settings.get(Settings.APP_STRINGS_INVALID_INPUT))
            )

        if type_base is str and field_descriptor.localizable:
            locale_index = int(state_data.get("locale_index"))

            value = state_data.get("value")
            if value:
                value = json.loads(value)
            else:
                value = {}

            value[list(LanguageBase.all_members.values())[locale_index].value] = (
                message.text
            )
            value = json.dumps(value, ensure_ascii=False)

            if locale_index < len(LanguageBase.all_members.values()) - 1:
                current_value = state_data.get("current_value")

                state_data.update({"value": value})
                # entity_descriptor = field_descriptor.entity_descriptor
                # entity_descriptor = get_entity_descriptor(app, callback_data)
                kwargs.update({"callback_data": callback_data})

                return await show_editor(
                    message=message,
                    locale_index=locale_index + 1,
                    field_descriptor=field_descriptor,
                    # entity_descriptor=entity_descriptor,
                    current_value=current_value,
                    value=value,
                    **kwargs,
                )

    else:
        field_descriptor = get_field_descriptor(app, callback_data)

        if callback_data.data:
            if callback_data.data == "skip":
                value = None
            else:
                value = callback_data.data
        else:
            value = state_data.get("value")

    kwargs.update(
        {
            "callback_data": callback_data,
        }
    )

    await process_field_edit_callback(
        message=message, value=value, field_descriptor=field_descriptor, **kwargs
    )


async def process_field_edit_callback(message: Message | CallbackQuery, **kwargs):
    user: UserBase = kwargs["user"]
    db_session: AsyncSession = kwargs["db_session"]
    callback_data: ContextData = kwargs.get("callback_data", None)
    state_data: dict = kwargs["state_data"]
    value = kwargs["value"]
    field_descriptor: FieldDescriptor = kwargs["field_descriptor"]

    if callback_data.context == CommandContext.SETTING_EDIT:
        if callback_data.data != "cancel":
            if await authorize_command(user=user, callback_data=callback_data):
                value = await deserialize(
                    session=db_session, type_=field_descriptor.type_, value=value
                )
                await Settings.set_param(field_descriptor, value)
            else:
                return await message.answer(
                    text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN))
                )

        clear_state(state_data=state_data)

        return await route_callback(message=message, back=True, **kwargs)

    elif callback_data.context in [
        CommandContext.ENTITY_CREATE,
        CommandContext.ENTITY_EDIT,
        CommandContext.ENTITY_FIELD_EDIT,
        CommandContext.COMMAND_FORM,
    ]:
        app: "QuickBot" = kwargs["app"]
        entity_descriptor = get_entity_descriptor(app, callback_data)

        entity_data = state_data.get("entity_data", {})
        entity_data[field_descriptor.name] = value

        if callback_data.context == CommandContext.COMMAND_FORM:
            field_sequence = list(field_descriptor.command.param_form.keys())
            current_index = field_sequence.index(callback_data.field_name)
            field_descriptors = field_descriptor.command.param_form
        else:
            form_name = (
                callback_data.form_params.split("&")[0]
                if callback_data.form_params
                else None
            )
            form: EntityForm = entity_descriptor.forms.get(
                form_name, entity_descriptor.default_form
            )

            if form.edit_field_sequence:
                field_sequence = form.edit_field_sequence
            else:
                context = BotContext(
                    db_session=kwargs["db_session"],
                    app=kwargs["app"],
                    app_state=kwargs["app_state"],
                    user=user,
                    message=message,
                )
                field_sequence = await build_field_sequence(
                    entity_descriptor=entity_descriptor,
                    user=user,
                    callback_data=callback_data,
                    state_data=state_data,
                    context=context,
                )

            current_index = (
                field_sequence.index(callback_data.field_name)
                if callback_data.context
                in [CommandContext.ENTITY_CREATE, CommandContext.ENTITY_EDIT]
                else 0
            )
            field_descriptors = entity_descriptor.fields_descriptors

        if callback_data.context == CommandContext.ENTITY_CREATE:
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
                prev_form_params = (
                    prev_callback_data.form_params.split("&")[1:]
                    if prev_callback_data.form_params
                    else []
                )
                prev_form_list: EntityList = entity_descriptor.lists.get(
                    prev_form_name, entity_descriptor.default_list
                )

                if prev_form_list.static_filters:
                    for filt in prev_form_list.static_filters:
                        if filt.value_type == "const":
                            entity_data[filt.field_name] = filt.value
                        elif len(prev_form_params) > filt.param_index:
                            entity_data[filt.field_name] = prev_form_params[
                                filt.param_index
                            ]

        if (
            callback_data.context
            in [
                CommandContext.ENTITY_CREATE,
                CommandContext.ENTITY_EDIT,
                CommandContext.COMMAND_FORM,
            ]
            and current_index < len(field_sequence) - 1
        ):
            # entity_data[field_descriptor.field_name] = value
            state_data.update({"entity_data": entity_data})

            next_field_name = field_sequence[current_index + 1]
            next_field_descriptor = field_descriptors[next_field_name]
            kwargs.update({"field_descriptor": next_field_descriptor})
            callback_data.field_name = next_field_name

            state_entity_val = entity_data.get(next_field_descriptor.field_name)

            current_value = (
                await deserialize(
                    session=db_session,
                    type_=next_field_descriptor.type_,
                    value=state_entity_val,
                )
                if state_entity_val
                else None
            )

            await show_editor(
                message=message,
                entity_descriptor=entity_descriptor,
                current_value=current_value,
                **kwargs,
            )

        else:
            # entity_data[field_descriptor.field_name] = value

            # What if user has several roles and each role has its own ownership field? Should we allow creation even
            # if user has no CREATE_ALL permission

            if callback_data.context in [
                CommandContext.ENTITY_CREATE,
                CommandContext.ENTITY_EDIT,
            ]:
                user_permissions = get_user_permissions(user, entity_descriptor)

                if entity_descriptor.rls_filters:
                    filters = []
                    if isinstance(entity_descriptor.rls_filters, Filter):
                        filters = [entity_descriptor.rls_filters]
                    elif (
                        isinstance(entity_descriptor.rls_filters, FilterExpression)
                        and entity_descriptor.rls_filters.operator == "and"
                        and all(
                            isinstance(f, Filter)
                            for f in entity_descriptor.rls_filters.filters
                        )
                    ):
                        filters = entity_descriptor.rls_filters.filters
                    filter_params = []
                    if filters and entity_descriptor.rls_filters_params:
                        if iscoroutinefunction(entity_descriptor.rls_filters_params):
                            filter_params = await entity_descriptor.rls_filters_params(
                                user
                            )
                        else:
                            filter_params = entity_descriptor.rls_filters_params(user)

                    for f in filters:
                        if f.operator == "==":
                            if isinstance(f.field, str):
                                field_name = f.field
                            else:
                                field_name = f.field(entity_descriptor.type_).key
                            entity_data[field_name] = (
                                f.value
                                if f.value_type == "const"
                                else filter_params[f.param_index]
                            )

            deser_entity_data = {
                key: await deserialize(
                    session=db_session,
                    type_=field_descriptors[key].type_,
                    value=value,
                )
                for key, value in entity_data.items()
            }

            context = BotContext(
                db_session=db_session,
                app=app,
                app_state=kwargs["app_state"],
                user=user,
                message=message,
            )

            if callback_data.context == CommandContext.ENTITY_CREATE:
                entity_type = entity_descriptor.type_
                user_permissions = get_user_permissions(user, entity_descriptor)
                if (
                    EntityPermission.CREATE_RLS not in user_permissions
                    and EntityPermission.CREATE_ALL not in user_permissions
                ):
                    return await message.answer(
                        text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN))
                    )

                new_entity = entity_type(**deser_entity_data)

                can_create = True

                if entity_descriptor.before_create_save:
                    if iscoroutinefunction(entity_descriptor.before_create_save):
                        can_create = await entity_descriptor.before_create_save(
                            new_entity,
                            context,
                        )
                    else:
                        can_create = entity_descriptor.before_create_save(
                            new_entity,
                            context,
                        )
                    if isinstance(can_create, str):
                        await message.answer(text=can_create, **{"show_alert": True})
                    elif not can_create:
                        await message.answer(
                            text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN)),
                            **{"show_alert": True},
                        )

                if isinstance(can_create, bool) and can_create:
                    new_entity = await entity_type.create(
                        session=db_session,
                        obj_in=new_entity,
                        commit=True,
                    )

                    if entity_descriptor.on_created:
                        if iscoroutinefunction(entity_descriptor.on_created):
                            await entity_descriptor.on_created(
                                new_entity,
                                context,
                            )
                        else:
                            entity_descriptor.on_created(
                                new_entity,
                                context,
                            )

                    form_name = (
                        callback_data.form_params.split("&")[0]
                        if callback_data.form_params
                        else None
                    )
                    form_list = entity_descriptor.lists.get(
                        form_name, entity_descriptor.default_list
                    )

                    state_data["navigation_context"] = ContextData(
                        command=CallbackCommand.ENTITY_ITEM,
                        entity_name=entity_descriptor.name,
                        form_params=form_list.item_form,
                        entity_id=str(new_entity.id),
                    ).pack()

                    state_data.update(state_data)

                    clear_state(state_data=state_data)
                    return await route_callback(message=message, back=False, **kwargs)

            elif callback_data.context in [
                CommandContext.ENTITY_EDIT,
                CommandContext.ENTITY_FIELD_EDIT,
            ]:
                entity_type = entity_descriptor.type_
                entity_id = int(callback_data.entity_id)
                entity = await entity_type.get(session=db_session, id=entity_id)
                if not entity:
                    return await message.answer(
                        text=(await Settings.get(Settings.APP_STRINGS_NOT_FOUND))
                    )

                if not await check_entity_permission(
                    entity=entity, user=user, permission=EntityPermission.UPDATE_RLS
                ):
                    return await message.answer(
                        text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN))
                    )

                old_values = {}

                for f in entity.bot_entity_descriptor.fields_descriptors.values():
                    value = getattr(entity, f.field_name)
                    if isinstance(value, InstrumentedList):
                        value = list(value)
                    old_values[f.field_name] = value

                new_values = old_values.copy()

                for key, value in deser_entity_data.items():
                    new_values[
                        entity.bot_entity_descriptor.fields_descriptors[key].field_name
                    ] = value

                can_update = True

                if entity_descriptor.before_update_save:
                    if iscoroutinefunction(entity_descriptor.before_update_save):
                        can_update = await entity_descriptor.before_update_save(
                            old_values,
                            new_values,
                            context,
                        )
                    else:
                        can_update = entity_descriptor.before_update_save(
                            old_values,
                            new_values,
                            context,
                        )
                    if isinstance(can_update, str):
                        await message.answer(text=can_update, **{"show_alert": True})
                    elif not can_update:
                        await message.answer(
                            text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN)),
                            **{"show_alert": True},
                        )

                if isinstance(can_update, bool) and can_update:
                    for attr in new_values:
                        if attr != "id":
                            setattr(entity, attr, new_values[attr])

                    await db_session.commit()
                    await db_session.refresh(entity)

                    if entity_descriptor.on_updated:
                        if iscoroutinefunction(entity_descriptor.on_updated):
                            await entity_descriptor.on_updated(
                                old_values,
                                entity,
                                context,
                            )
                        else:
                            entity_descriptor.on_updated(
                                old_values,
                                entity,
                                context,
                            )
                else:
                    await db_session.rollback()

            elif callback_data.context == CommandContext.COMMAND_FORM:
                clear_state(state_data=state_data)
                state_data["entity_data"] = entity_data

                kwargs.update(
                    {
                        "callback_data": ContextData(
                            command=CallbackCommand.USER_COMMAND,
                            user_command=callback_data.user_command,
                        )
                    }
                )

                cmd = app.bot_commands.get(callback_data.user_command.split("&")[0])

                return await command_handler(message=message, cmd=cmd, **kwargs)

            clear_state(state_data=state_data)

            await route_callback(message=message, back=True, **kwargs)
