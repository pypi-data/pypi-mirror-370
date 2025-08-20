from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import TYPE_CHECKING

from ..context import ContextData, CallbackCommand
from ...command_context_filter import CallbackCommandFilter
from ....model.user import UserBase
from ....model.settings import Settings
from ....model.view_setting import ViewSetting
from ....utils.main import (
    get_send_message,
    get_entity_descriptor,
    get_field_descriptor,
)
from ....utils.serialization import deserialize
from ..editors.entity import render_entity_picker
from .routing import route_callback

if TYPE_CHECKING:
    from ....main import QuickBot


router = Router()


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.VIEW_FILTER_EDIT)
)
async def view_filter_edit(query: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    args = callback_data.data.split("&")
    page = int(args[0])
    cmd = None
    if len(args) > 1:
        cmd = args[1]

    db_session: AsyncSession = kwargs["db_session"]
    app: "QuickBot" = kwargs["app"]
    user: UserBase = kwargs["user"]
    entity_descriptor = get_entity_descriptor(app=app, callback_data=callback_data)

    if cmd in ["cancel", "clear"]:
        if cmd == "clear":
            await ViewSetting.set_filter(
                session=db_session,
                user_id=user.id,
                entity_name=entity_descriptor.class_name,
                filter=None,
            )

        context_data_bak = state_data.pop("context_data_bak", None)
        if context_data_bak:
            state_data["context_data"] = context_data_bak
            context_data = ContextData.unpack(context_data_bak)

            field_descriptor = get_field_descriptor(app, context_data)
            edit_prompt = state_data["edit_prompt"]
            current_value = await deserialize(
                session=db_session,
                type_=field_descriptor.type_,
                value=state_data["value"],
            )
            page = int(state_data.pop("page"))
            kwargs.pop("callback_data")

            return await render_entity_picker(
                field_descriptor=field_descriptor,
                message=query,
                callback_data=context_data,
                current_value=current_value,
                edit_prompt=edit_prompt,
                page=page,
                **kwargs,
            )

        else:
            state_data.pop("context_data", None)
            return await route_callback(message=query, back=False, **kwargs)

    # await save_navigation_context(callback_data = callback_data, state = state)
    old_context_data = state_data.get("context_data")
    await state.update_data(
        {
            "context_data": callback_data.pack(),
            "context_data_bak": old_context_data,
            "page": page,
        }
    )

    send_message = get_send_message(query)

    await send_message(
        text=await Settings.get(Settings.APP_STRINGS_VIEW_FILTER_EDIT_PROMPT),
        reply_markup=InlineKeyboardBuilder()
        .row(
            InlineKeyboardButton(
                text=await Settings.get(Settings.APP_STRINGS_CANCEL_BTN),
                callback_data=ContextData(
                    command=CallbackCommand.VIEW_FILTER_EDIT,
                    entity_name=entity_descriptor.name,
                    data=f"{page}&cancel",
                ).pack(),
            ),
            InlineKeyboardButton(
                text=await Settings.get(Settings.APP_STRINGS_CLEAR_BTN),
                callback_data=ContextData(
                    command=CallbackCommand.VIEW_FILTER_EDIT,
                    entity_name=entity_descriptor.name,
                    data=f"{page}&clear",
                ).pack(),
            ),
        )
        .as_markup(),
    )


@router.message(CallbackCommandFilter(command=CallbackCommand.VIEW_FILTER_EDIT))
async def view_filter_edit_input(message: Message, **kwargs):
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data
    callback_data = ContextData.unpack(state_data["context_data"])
    db_session: AsyncSession = kwargs["db_session"]
    user: UserBase = kwargs["user"]
    app: "QuickBot" = kwargs["app"]
    entity_descriptor = get_entity_descriptor(app=app, callback_data=callback_data)
    filter = message.text
    await ViewSetting.set_filter(
        session=db_session,
        user_id=user.id,
        entity_name=entity_descriptor.class_name,
        filter=filter,
    )

    # state_data.pop("context_data")
    # return await route_callback(message = message, back = False, **kwargs)

    context_data_bak = state_data.pop("context_data_bak", None)
    if context_data_bak:
        state_data["context_data"] = context_data_bak
        context_data = ContextData.unpack(context_data_bak)
        field_descriptor = get_field_descriptor(app, context_data)
        edit_prompt = state_data["edit_prompt"]
        current_value = await deserialize(
            session=db_session, type_=field_descriptor.type_, value=state_data["value"]
        )
        page = int(state_data.pop("page"))

        return await render_entity_picker(
            field_descriptor=field_descriptor,
            message=message,
            callback_data=context_data,
            current_value=current_value,
            edit_prompt=edit_prompt,
            page=page,
            **kwargs,
        )

    else:
        state_data.pop("context_data", None)
        return await route_callback(message=message, back=False, **kwargs)
