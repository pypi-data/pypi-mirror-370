from inspect import iscoroutinefunction
from typing import TYPE_CHECKING
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from logging import getLogger
from sqlalchemy.orm.collections import InstrumentedList
from sqlmodel.ext.asyncio.session import AsyncSession
from quickbot.model.descriptors import BotContext, EntityForm

from ....model import EntityPermission
from ....model.settings import Settings
from ....model.user import UserBase
from ....model.permissions import check_entity_permission
from ....utils.main import (
    build_field_sequence,
    get_field_descriptor,
    clear_state,
)
from ....utils.serialization import deserialize, serialize
from ..context import ContextData, CallbackCommand, CommandContext
from ....auth import authorize_command
from ....utils.navigation import (
    get_navigation_context,
    save_navigation_context,
)
from ..forms.entity_form import entity_item
from .common import show_editor

from ..menu.parameters import parameters_menu
from .string import router as string_editor_router
from .date import router as date_picker_router
from .boolean import router as bool_editor_router
from .entity import router as entity_picker_router

if TYPE_CHECKING:
    from ....main import QuickBot


logger = getLogger(__name__)
router = Router()


@router.callback_query(ContextData.filter(F.command == CallbackCommand.FIELD_EDITOR))
async def field_editor_callback(query: CallbackQuery, **kwargs):
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    await field_editor(message=query, **kwargs)


async def field_editor(message: Message | CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs.get("callback_data", None)
    db_session: AsyncSession = kwargs["db_session"]
    user: UserBase = kwargs["user"]
    app: "QuickBot" = kwargs["app"]
    state: FSMContext = kwargs["state"]

    state_data: dict = kwargs["state_data"]
    entity_data = state_data.get("entity_data")

    for key in ["current_value", "value", "locale_index"]:
        if key in state_data:
            state_data.pop(key)

    kwargs["state_data"] = state_data

    entity_descriptor = None

    if callback_data.context == CommandContext.SETTING_EDIT:
        field_descriptor = get_field_descriptor(app, callback_data)

        if field_descriptor.type_ is bool:
            if await authorize_command(user=user, callback_data=callback_data):
                await Settings.set_param(
                    field_descriptor, not await Settings.get(field_descriptor)
                )
            else:
                return await message.answer(
                    text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN))
                )

            stack, context = get_navigation_context(state_data=state_data)

            return await parameters_menu(
                message=message, navigation_stack=stack, **kwargs
            )

        current_value = await Settings.get(field_descriptor, all_locales=True)
    else:
        field_descriptor = get_field_descriptor(app, callback_data)
        entity_descriptor = field_descriptor.entity_descriptor

        current_value = None

        context = BotContext(
            db_session=db_session,
            app=app,
            app_state=kwargs["app_state"],
            user=user,
            message=message,
        )

        if (
            field_descriptor.type_base is bool
            and callback_data.context == CommandContext.ENTITY_FIELD_EDIT
        ):
            entity = await entity_descriptor.type_.get(
                session=db_session, id=int(callback_data.entity_id)
            )
            if await check_entity_permission(
                entity=entity, user=user, permission=EntityPermission.UPDATE_RLS
            ):
                old_values = {}

                for f in entity.bot_entity_descriptor.fields_descriptors.values():
                    value = getattr(entity, f.field_name)
                    if isinstance(value, InstrumentedList):
                        value = list(value)
                    old_values[f.field_name] = value

                new_values = old_values.copy()

                current_value: bool = (
                    getattr(entity, field_descriptor.field_name) or False
                )
                new_values[field_descriptor.field_name] = not current_value

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

                    stack, context_data = get_navigation_context(state_data=state_data)
                    kwargs.update({"callback_data": context_data})
                    await state.set_data(state_data)

                    return await entity_item(
                        query=message, navigation_stack=stack, **kwargs
                    )

            return

        if not entity_data and callback_data.context in [
            CommandContext.ENTITY_EDIT,
            CommandContext.ENTITY_FIELD_EDIT,
        ]:
            entity = await entity_descriptor.type_.get(
                session=kwargs["db_session"], id=int(callback_data.entity_id)
            )
            if await check_entity_permission(
                entity=entity, user=user, permission=EntityPermission.READ_RLS
            ):
                if entity:
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
                        field_sequence = await build_field_sequence(
                            entity_descriptor=entity_descriptor,
                            user=user,
                            callback_data=callback_data,
                            state_data=state_data,
                            context=context,
                        )
                    entity_data = {
                        key: serialize(
                            getattr(
                                entity,
                                entity_descriptor.fields_descriptors[key].field_name,
                            ),
                            entity_descriptor.fields_descriptors[key],
                        )
                        for key in (
                            field_sequence
                            if callback_data.context == CommandContext.ENTITY_EDIT
                            else [callback_data.field_name]
                        )
                    }
                    state_data.update({"entity_data": entity_data})

        if callback_data.context == CommandContext.ENTITY_CREATE:
            if entity_descriptor.before_create:
                if iscoroutinefunction(entity_descriptor.before_create):
                    can_create = await entity_descriptor.before_create(
                        context,
                    )
                else:
                    can_create = entity_descriptor.before_create(
                        context,
                    )
                if isinstance(can_create, str):
                    return await message.answer(text=can_create, **{"show_alert": True})
                elif not can_create:
                    return await message.answer(
                        text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN)),
                        **{"show_alert": True},
                    )

        if entity_data:
            current_value = await deserialize(
                session=db_session,
                type_=field_descriptor.type_,
                value=entity_data.get(callback_data.field_name),
            )

    kwargs.update({"field_descriptor": field_descriptor})
    save_navigation_context(state_data=state_data, callback_data=callback_data)

    await show_editor(message=message, current_value=current_value, **kwargs)


@router.callback_query(ContextData.filter(F.command == CallbackCommand.DELETE_MESSAGE))
async def delete_message_callback(query: CallbackQuery, **kwargs):
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    context_data: ContextData = kwargs["callback_data"]
    clear_nav = context_data.data == "clear_nav"
    clear_state(state_data=state_data, clear_nav=clear_nav)
    await state.set_data(state_data)

    await query.message.delete()


router.include_routers(
    string_editor_router,
    date_picker_router,
    bool_editor_router,
    entity_picker_router,
)
