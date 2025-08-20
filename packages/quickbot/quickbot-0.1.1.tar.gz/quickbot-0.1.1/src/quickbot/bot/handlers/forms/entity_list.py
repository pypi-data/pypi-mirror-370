from typing import TYPE_CHECKING
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger
from sqlmodel.ext.asyncio.session import AsyncSession

from ....model.bot_entity import BotEntity
from ....model.settings import Settings
from ....model.user import UserBase
from ....model.view_setting import ViewSetting
from ....model.descriptors import (
    BotContext,
    EntityForm,
    EntityList,
)
from ....model import EntityPermission
from ....utils.main import (
    get_user_permissions,
    get_send_message,
    clear_state,
    get_entity_descriptor,
    get_callable_str,
    build_field_sequence,
    prepare_static_filter,
)
from ..context import ContextData, CallbackCommand, CommandContext
from ..common.pagination import add_pagination_controls
from ..common.filtering import add_filter_controls
from ....utils.navigation import pop_navigation_context, save_navigation_context

if TYPE_CHECKING:
    from ....main import QuickBot


logger = getLogger(__name__)
router = Router()


@router.callback_query(ContextData.filter(F.command == CallbackCommand.ENTITY_LIST))
async def entity_list_callback(query: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]

    if callback_data.data == "skip":
        return

    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    clear_state(state_data=state_data)
    stack = save_navigation_context(callback_data=callback_data, state_data=state_data)
    await state.set_data(state_data)

    await entity_list(message=query, navigation_stack=stack, **kwargs)


def calc_total_pages(items_count: int, page_size: int) -> int:
    return max(items_count // page_size + (1 if items_count % page_size else 0), 1)


async def entity_list(
    message: CallbackQuery | Message,
    callback_data: ContextData,
    db_session: AsyncSession,
    user: UserBase,
    app: "QuickBot",
    navigation_stack: list[ContextData],
    **kwargs,
):
    page = int(callback_data.data or "1")

    entity_descriptor = get_entity_descriptor(app, callback_data)
    user_permissions = get_user_permissions(user, entity_descriptor)
    entity_type = entity_descriptor.type_
    form_params = (
        callback_data.form_params.split("&") if callback_data.form_params else []
    )
    form_name = form_params.pop(0) if form_params else None
    form_list: EntityList = entity_descriptor.lists.get(
        form_name, entity_descriptor.default_list
    )
    form_item: EntityForm = entity_descriptor.forms.get(
        form_list.item_form, entity_descriptor.default_form
    )

    keyboard_builder = InlineKeyboardBuilder()
    context = BotContext(
        db_session=db_session,
        app=app,
        app_state=kwargs["app_state"],
        user=user,
        message=message,
    )

    if (
        EntityPermission.CREATE_RLS in user_permissions
        or EntityPermission.CREATE_ALL in user_permissions
    ) and form_list.show_add_new_button:
        if form_item.edit_field_sequence:
            field_sequence = form_item.edit_field_sequence
        else:
            field_sequence = await build_field_sequence(
                entity_descriptor=entity_descriptor,
                user=user,
                callback_data=callback_data,
                state_data=kwargs["state_data"],
                context=context,
            )
        keyboard_builder.row(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_ADD_BTN)),
                callback_data=ContextData(
                    command=CallbackCommand.FIELD_EDITOR,
                    context=CommandContext.ENTITY_CREATE,
                    entity_name=entity_descriptor.name,
                    field_name=field_sequence[0],
                    form_params=form_list.item_form,
                ).pack(),
            )
        )

    if form_list.filtering:
        entity_filter = await ViewSetting.get_filter(
            session=db_session,
            user_id=user.id,
            entity_name=entity_descriptor.class_name,
        )
    else:
        entity_filter = None

    list_all = (
        EntityPermission.LIST_ALL in user_permissions
        or EntityPermission.READ_ALL in user_permissions
    )
    if (
        list_all
        or EntityPermission.LIST_RLS in user_permissions
        or EntityPermission.READ_RLS in user_permissions
    ):
        if form_list.pagination:
            page_size = await Settings.get(Settings.PAGE_SIZE)
            items_count = await entity_type.get_count(
                session=db_session,
                static_filter=await prepare_static_filter(
                    db_session=db_session,
                    entity_descriptor=entity_descriptor,
                    static_filters=form_list.static_filters,
                    params=form_params,
                ),
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

        items = await entity_type.get_multi(
            session=db_session,
            order_by=form_list.order_by,
            static_filter=await prepare_static_filter(
                db_session=db_session,
                entity_descriptor=entity_descriptor,
                static_filters=form_list.static_filters,
                params=form_params,
            ),
            filter=entity_filter,
            filter_fields=form_list.filtering_fields,
            user=user if not list_all else None,
            skip=skip,
            limit=limit,
        )
    else:
        items = list[BotEntity]()
        items_count = 0
        total_pages = 1
        page = 1

    for item in items:
        caption = None

        if form_list.item_repr:
            caption = await get_callable_str(
                callable_str=form_list.item_repr,
                context=context,
                entity=item,
            )
        elif entity_descriptor.item_repr:
            caption = await get_callable_str(
                callable_str=entity_descriptor.item_repr,
                context=context,
                entity=item,
            )
        elif entity_descriptor.full_name:
            caption = f"{
                await get_callable_str(
                    callable_str=entity_descriptor.full_name,
                    context=context,
                    descriptor=entity_descriptor,
                    entity=item,
                )
            }: {item.id}"

        if not caption:
            caption = f"{entity_descriptor.name}: {item.id}"

        keyboard_builder.row(
            InlineKeyboardButton(
                text=caption,
                callback_data=ContextData(
                    command=CallbackCommand.ENTITY_ITEM,
                    entity_name=entity_descriptor.name,
                    form_params=form_list.item_form,
                    entity_id=str(item.id),
                ).pack(),
            )
        )

    if form_list.pagination:
        add_pagination_controls(
            keyboard_builder=keyboard_builder,
            callback_data=callback_data,
            total_pages=total_pages,
            command=CallbackCommand.ENTITY_LIST,
            page=page,
        )

    if form_list.filtering and form_list.filtering_fields:
        await add_filter_controls(
            keyboard_builder=keyboard_builder,
            entity_descriptor=entity_descriptor,
            context=context,
            filter=entity_filter,
            filtering_fields=form_list.filtering_fields,
        )

    navigation_context = pop_navigation_context(navigation_stack)
    if navigation_context:
        keyboard_builder.row(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_BACK_BTN)),
                callback_data=navigation_context.pack(),
            )
        )

    if form_list.caption:
        entity_text = await get_callable_str(
            callable_str=form_list.caption,
            context=context,
            descriptor=entity_descriptor,
        )
    else:
        if entity_descriptor.full_name_plural:
            entity_text = await get_callable_str(
                callable_str=entity_descriptor.full_name_plural,
                context=context,
                descriptor=entity_descriptor,
            )
        else:
            entity_text = entity_descriptor.name

        if entity_descriptor.ui_description:
            entity_text = f"{entity_text} {
                await get_callable_str(
                    callable_str=entity_descriptor.ui_description,
                    context=context,
                    descriptor=entity_descriptor,
                )
            }"

    # state: FSMContext = kwargs["state"]
    # state_data = kwargs["state_data"]
    # await state.set_data(state_data)

    send_message = get_send_message(message)

    await send_message(text=entity_text, reply_markup=keyboard_builder.as_markup())
