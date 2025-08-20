from inspect import iscoroutinefunction
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger
from sqlmodel import column
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import TYPE_CHECKING

from ....model.bot_entity import BotEntity

# from ....model.owned_bot_entity import OwnedBotEntity
from ....model.bot_enum import BotEnum
from ....model.settings import Settings
from ....model.user import UserBase
from ....model.view_setting import ViewSetting
from ....model.descriptors import BotContext, EntityList, FieldDescriptor
from ....model import EntityPermission
from ....utils.main import (
    get_user_permissions,
    get_send_message,
    get_field_descriptor,
    get_callable_str,
    prepare_static_filter,
)
from ....utils.serialization import serialize, deserialize
from ..context import ContextData, CallbackCommand
from ..common.pagination import add_pagination_controls
from ..common.filtering import add_filter_controls
from .wrapper import wrap_editor

if TYPE_CHECKING:
    from ....main import QuickBot

logger = getLogger(__name__)
router = Router()


async def entity_picker(
    message: Message | CallbackQuery,
    field_descriptor: FieldDescriptor,
    edit_prompt: str,
    current_value: BotEntity | BotEnum | list[BotEntity] | list[BotEnum],
    **kwargs,
):
    state_data: dict = kwargs["state_data"]

    state_data.update(
        {
            "current_value": serialize(current_value, field_descriptor),
            "value": serialize(current_value, field_descriptor),
            "edit_prompt": edit_prompt,
        }
    )

    await render_entity_picker(
        field_descriptor=field_descriptor,
        message=message,
        current_value=current_value,
        edit_prompt=edit_prompt,
        **kwargs,
    )


def calc_total_pages(items_count: int, page_size: int) -> int:
    return max(items_count // page_size + (1 if items_count % page_size else 0), 1)


async def render_entity_picker(
    *,
    field_descriptor: FieldDescriptor,
    message: Message | CallbackQuery,
    callback_data: ContextData,
    user: UserBase,
    db_session: AsyncSession,
    state: FSMContext,
    current_value: BotEntity | BotEnum | list[BotEntity] | list[BotEnum],
    edit_prompt: str,
    page: int = 1,
    **kwargs,
):
    if callback_data.command in [
        CallbackCommand.ENTITY_PICKER_PAGE,
        CallbackCommand.ENTITY_PICKER_TOGGLE_ITEM,
    ]:
        page = int(callback_data.data.split("&")[0])

    type_ = field_descriptor.type_base
    is_list = field_descriptor.is_list

    if not issubclass(type_, BotEntity) and not issubclass(type_, BotEnum):
        raise ValueError("Unsupported type")

    page_size = await Settings.get(Settings.PAGE_SIZE)
    form_list = None

    context = BotContext(
        db_session=db_session,
        app=kwargs["app"],
        app_state=kwargs["app_state"],
        user=user,
        message=message,
    )

    entity = None

    if issubclass(type_, BotEnum):
        items_count = len(type_.all_members)
        total_pages = calc_total_pages(items_count, page_size)
        page = min(page, total_pages)
        if isinstance(field_descriptor.options, list):
            enum_items = field_descriptor.options[
                page_size * (page - 1) : page_size * page
            ]
        elif callable(field_descriptor.options):
            if callback_data.entity_id:
                entity = await field_descriptor.entity_descriptor.type_.get(
                    session=db_session, id=callback_data.entity_id
                )
            if iscoroutinefunction(field_descriptor.options):
                enum_items = (await field_descriptor.options(entity, context)) or []
            else:
                enum_items = field_descriptor.options(entity, context) or []
            enum_items = enum_items[page_size * (page - 1) : page_size * page]
        else:
            enum_items = list(type_.all_members.values())[
                page_size * (page - 1) : page_size * page
            ]
        items = []
        for it_row in enum_items:
            if not isinstance(it_row, list):
                it_row = [it_row]
            item_row = []
            for item in it_row:
                if isinstance(item, tuple):
                    item_value, item_text = item
                else:
                    item_value = item
                    item_text = item.localized(user.lang)
                item_row.append(
                    {
                        "text": f"{'' if not is_list else '[✓] ' if item_value in (current_value or []) else '[  ] '}{item_text}",
                        "value": item_value.value,
                    }
                )
            items.append(item_row)

    elif issubclass(type_, BotEntity):
        ep_form = "default"
        ep_form_params = []

        if field_descriptor.ep_form:
            if callable(field_descriptor.ep_form):
                if iscoroutinefunction(field_descriptor.ep_form):
                    ep_form = await field_descriptor.ep_form(context)
                else:
                    ep_form = field_descriptor.ep_form(context)

            else:
                ep_form = field_descriptor.ep_form

            ep_form_list = ep_form.split("&")

            ep_form = ep_form_list[0]
            ep_form_params = ep_form_list[1:] if len(ep_form_list) > 1 else []

        form_list: EntityList = type_.bot_entity_descriptor.lists.get(
            ep_form, type_.bot_entity_descriptor.default_list
        )
        permissions = get_user_permissions(user, type_.bot_entity_descriptor)
        if form_list.filtering:
            entity_filter = await ViewSetting.get_filter(
                session=db_session,
                user_id=user.id,
                entity_name=type_.bot_entity_descriptor.class_name,
            )
        else:
            entity_filter = None
        list_all = EntityPermission.LIST_ALL in permissions

        if list_all or EntityPermission.LIST_RLS in permissions:
            if (
                field_descriptor.ep_parent_field
                and field_descriptor.ep_child_field
                and callback_data.entity_id
            ):
                if callable(field_descriptor.ep_parent_field):
                    parent_field = field_descriptor.ep_parent_field(
                        field_descriptor.entity_descriptor.type_
                    ).key
                else:
                    parent_field = field_descriptor.ep_parent_field

                if callable(field_descriptor.ep_child_field):
                    child_field = field_descriptor.ep_child_field(
                        field_descriptor.entity_descriptor.type_
                    ).key
                else:
                    child_field = field_descriptor.ep_child_field

                entity = await field_descriptor.entity_descriptor.type_.get(
                    session=db_session, id=callback_data.entity_id
                )
                value = getattr(entity, parent_field)
                ext_filter = column(child_field).__eq__(value)

            else:
                ext_filter = None

            if form_list.pagination:
                items_count = await type_.get_count(
                    session=db_session,
                    static_filter=await prepare_static_filter(
                        db_session=db_session,
                        entity_descriptor=type_.bot_entity_descriptor,
                        static_filters=form_list.static_filters,
                        params=ep_form_params,
                    ),
                    ext_filter=ext_filter,
                    filter=entity_filter,
                    filter_fields=form_list.filtering_fields,
                    user=user if not list_all else None,
                )
                total_pages = calc_total_pages(items_count, page_size)
                page = min(page, total_pages)
                skip = page_size * (page - 1)
                limit = page_size
            else:
                skip = 0
                limit = None
            entity_items = await type_.get_multi(
                session=db_session,
                order_by=form_list.order_by,
                static_filter=await prepare_static_filter(
                    db_session=db_session,
                    entity_descriptor=type_.bot_entity_descriptor,
                    static_filters=form_list.static_filters,
                    params=ep_form_params,
                ),
                ext_filter=ext_filter,
                filter=entity_filter,
                user=user if not list_all else None,
                skip=skip,
                limit=limit,
            )
        else:
            items_count = 0
            total_pages = 1
            page = 1
            entity_items = list[BotEntity]()

        items = [
            [
                {
                    "text": f"{
                        ''
                        if not is_list
                        else '[✓] '
                        if item in (current_value or [])
                        else '[  ] '
                    }{
                        await get_callable_str(
                            callable_str=type_.bot_entity_descriptor.item_repr,
                            context=context,
                            entity=item,
                        )
                        if type_.bot_entity_descriptor.item_repr
                        else await get_callable_str(
                            callable_str=type_.bot_entity_descriptor.full_name,
                            context=context,
                            descriptor=type_.bot_entity_descriptor,
                        )
                        if type_.bot_entity_descriptor.full_name
                        else f'{type_.bot_entity_descriptor.name}: {str(item.id)}'
                    }",
                    "value": str(item.id),
                }
            ]
            for item in entity_items
        ]

    keyboard_builder = InlineKeyboardBuilder()

    for item_row in items:
        btn_row = []
        for item in item_row:
            btn_row.append(
                InlineKeyboardButton(
                    text=item["text"],
                    callback_data=ContextData(
                        command=(
                            CallbackCommand.ENTITY_PICKER_TOGGLE_ITEM
                            if is_list
                            else CallbackCommand.FIELD_EDITOR_CALLBACK
                        ),
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data=f"{page}&{item['value']}" if is_list else item["value"],
                    ).pack(),
                )
            )
        keyboard_builder.row(*btn_row)

    if form_list and form_list.pagination:
        add_pagination_controls(
            keyboard_builder=keyboard_builder,
            callback_data=callback_data,
            total_pages=total_pages,
            command=CallbackCommand.ENTITY_PICKER_PAGE,
            page=page,
        )

    if (
        issubclass(type_, BotEntity)
        and form_list.filtering
        and form_list.filtering_fields
    ):
        await add_filter_controls(
            keyboard_builder=keyboard_builder,
            entity_descriptor=type_.bot_entity_descriptor,
            context=context,
            filter=entity_filter,
            filtering_fields=form_list.filtering_fields,
        )

    if is_list:
        keyboard_builder.row(
            InlineKeyboardButton(
                text=await Settings.get(Settings.APP_STRINGS_DONE_BTN),
                callback_data=ContextData(
                    command=CallbackCommand.FIELD_EDITOR_CALLBACK,
                    context=callback_data.context,
                    entity_name=callback_data.entity_name,
                    entity_id=callback_data.entity_id,
                    field_name=callback_data.field_name,
                    form_params=callback_data.form_params,
                    user_command=callback_data.user_command,
                ).pack(),
            )
        )

    state_data = kwargs["state_data"]

    await wrap_editor(
        keyboard_builder=keyboard_builder,
        field_descriptor=field_descriptor,
        callback_data=callback_data,
        state_data=state_data,
        user=user,
        context=context,
        entity=entity,
    )

    await state.set_data(state_data)

    if message:
        send_message = get_send_message(message)
        await send_message(text=edit_prompt, reply_markup=keyboard_builder.as_markup())
    else:
        app: "QuickBot" = kwargs["app"]
        await app.bot.send_message(
            chat_id=user.id, text=edit_prompt, reply_markup=keyboard_builder.as_markup()
        )


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.ENTITY_PICKER_PAGE)
)
@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.ENTITY_PICKER_TOGGLE_ITEM)
)
async def entity_picker_callback(
    query: CallbackQuery,
    callback_data: ContextData,
    db_session: AsyncSession,
    app: "QuickBot",
    state: FSMContext,
    **kwargs,
):
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    field_descriptor = get_field_descriptor(app=app, callback_data=callback_data)

    # current_value = await deserialize(session = db_session, type_ = field_descriptor.type_, value = state_data["current_value"])
    edit_prompt = state_data["edit_prompt"]
    value = await deserialize(
        session=db_session, type_=field_descriptor.type_, value=state_data["value"]
    )

    if callback_data.command == CallbackCommand.ENTITY_PICKER_TOGGLE_ITEM:
        page, id_value = callback_data.data.split("&")
        page = int(page)
        type_ = field_descriptor.type_base
        if issubclass(type_, BotEnum):
            item = type_(id_value)
            if item in value:
                value.remove(item)
            else:
                value.append(item)
        else:
            item = await type_.get(session=db_session, id=int(id_value))
            if item in value:
                value.remove(item)
            else:
                value.append(item)

        state_data.update({"value": serialize(value, field_descriptor)})
    elif callback_data.command == CallbackCommand.ENTITY_PICKER_PAGE:
        if callback_data.data == "skip":
            return
        page = int(callback_data.data)
    else:
        raise ValueError("Unsupported command")

    await render_entity_picker(
        field_descriptor=field_descriptor,
        message=query,
        callback_data=callback_data,
        current_value=value,
        edit_prompt=edit_prompt,
        db_session=db_session,
        app=app,
        state=state,
        page=page,
        **kwargs,
    )
