from inspect import iscoroutinefunction
from typing import TYPE_CHECKING
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger
from sqlmodel.ext.asyncio.session import AsyncSession

from ....model.descriptors import (
    EntityForm,
    FieldEditButton,
    CommandButton,
    InlineButton,
    BotContext,
)
from ....model.bot_entity import BotEntity
from ....model.settings import Settings
from ....model.user import UserBase
from ....model import EntityPermission
from ....model.permissions import check_entity_permission
from ....utils.main import (
    get_send_message,
    clear_state,
    get_value_repr,
    get_callable_str,
    get_entity_descriptor,
    build_field_sequence,
)
from ..context import ContextData, CallbackCommand, CommandContext
from ....utils.navigation import (
    pop_navigation_context,
    save_navigation_context,
)

if TYPE_CHECKING:
    from ....main import QuickBot


logger = getLogger(__name__)
router = Router()


@router.callback_query(ContextData.filter(F.command == CallbackCommand.ENTITY_ITEM))
async def entity_item_callback(query: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    clear_state(state_data=state_data)
    stack = save_navigation_context(callback_data=callback_data, state_data=state_data)
    await state.set_data(state_data)

    await entity_item(query=query, navigation_stack=stack, **kwargs)


async def entity_item(
    query: CallbackQuery,
    callback_data: ContextData,
    db_session: AsyncSession,
    user: UserBase,
    app: "QuickBot",
    navigation_stack: list[ContextData],
    **kwargs,
):
    entity_descriptor = get_entity_descriptor(app, callback_data)
    # user_permissions = get_user_permissions(user, entity_descriptor)
    entity_type = entity_descriptor.type_

    keyboard_builder = InlineKeyboardBuilder()

    entity_item = await entity_type.get(session=db_session, id=callback_data.entity_id)

    # state: FSMContext = kwargs["state"]
    state_data = kwargs["state_data"]
    # await state.set_data(state_data)

    if not entity_item and query:
        return await query.answer(
            text=(await Settings.get(Settings.APP_STRINGS_NOT_FOUND))
        )

    # is_owned = issubclass(entity_type, OwnedBotEntity)

    if query and not await check_entity_permission(
        entity=entity_item, user=user, permission=EntityPermission.READ_RLS
    ):
        return await query.answer(
            text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN))
        )

    can_edit = await check_entity_permission(
        entity=entity_item, user=user, permission=EntityPermission.UPDATE_RLS
    )

    form: EntityForm = entity_descriptor.forms.get(
        callback_data.form_params, entity_descriptor.default_form
    )

    context = BotContext(
        db_session=db_session,
        app=app,
        app_state=kwargs["app_state"],
        user=user,
        message=query,
        default_handler=item_repr,
    )

    if form.before_open:
        if iscoroutinefunction(form.before_open):
            await form.before_open(entity_item, context)
        else:
            form.before_open(entity_item, context)

    if form.form_buttons:
        for edit_buttons_row in form.form_buttons:
            btn_row = []
            for button in edit_buttons_row:
                if button.visibility and not button.visibility(entity_item, context):
                    continue

                if isinstance(button, FieldEditButton) and can_edit:
                    if isinstance(button.field, str):
                        field_name = button.field
                    else:
                        field_name = button.field(entity_descriptor.type_).key
                        for fd in entity_descriptor.fields_descriptors.values():
                            if fd.field_name == field_name:
                                field_name = fd.name
                                break
                    btn_caption = button.caption
                    if field_name in entity_descriptor.fields_descriptors:
                        field_descriptor = entity_descriptor.fields_descriptors[
                            field_name
                        ]
                        field_value = getattr(entity_item, field_descriptor.field_name)
                        if btn_caption:
                            btn_text = await get_callable_str(
                                callable_str=btn_caption,
                                context=context,
                                entity=entity_item,
                            )
                        else:
                            if field_descriptor.type_base is bool:
                                btn_text = f"{'[✓] ' if field_value else '[  ] '}{
                                    await get_callable_str(
                                        callable_str=field_descriptor.caption,
                                        context=context,
                                        descriptor=field_descriptor,
                                    )
                                    if field_descriptor.caption
                                    else field_name
                                }"
                            else:
                                btn_text = f"{
                                    field_descriptor.icon
                                    if field_descriptor.icon
                                    else '✏️'
                                } {
                                    await get_callable_str(
                                        callable_str=field_descriptor.caption,
                                        context=context,
                                        descriptor=field_descriptor,
                                    )
                                    if field_descriptor.caption
                                    else field_name
                                }"
                        btn_row.append(
                            InlineKeyboardButton(
                                text=btn_text,
                                callback_data=ContextData(
                                    command=CallbackCommand.FIELD_EDITOR,
                                    context=CommandContext.ENTITY_FIELD_EDIT,
                                    entity_name=entity_descriptor.name,
                                    entity_id=str(entity_item.id),
                                    field_name=field_name,
                                ).pack(),
                            )
                        )

                elif isinstance(button, CommandButton):
                    btn_caption = button.caption

                    btn_text = await get_callable_str(
                        callable_str=btn_caption,
                        context=context,
                        entity=entity_item,
                    )

                    if isinstance(button.command, ContextData):
                        btn_cdata = button.command
                    elif callable(button.command):
                        if iscoroutinefunction(button.command):
                            btn_cdata = await button.command(entity_item, context)
                        else:
                            btn_cdata = button.command(entity_item, context)
                    elif isinstance(button.command, str):
                        btn_cdata = ContextData(
                            command=CallbackCommand.USER_COMMAND,
                            user_command=button.command,
                        )

                    btn_row.append(
                        InlineKeyboardButton(
                            text=btn_text,
                            callback_data=btn_cdata.pack(),
                        )
                    )

                elif isinstance(button, InlineButton):
                    if isinstance(button.inline_button, InlineKeyboardButton):
                        btn_row.append(button.inline_button)
                    elif callable(button.inline_button):
                        if iscoroutinefunction(button.inline_button):
                            btn_row.append(
                                await button.inline_button(entity_item, context)
                            )
                        else:
                            btn_row.append(button.inline_button(entity_item, context))

            if btn_row:
                keyboard_builder.row(*btn_row)

    edit_delete_row = []
    if can_edit and form.show_edit_button:
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
        edit_delete_row.append(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_EDIT_BTN)),
                callback_data=ContextData(
                    command=CallbackCommand.FIELD_EDITOR,
                    context=CommandContext.ENTITY_EDIT,
                    entity_name=entity_descriptor.name,
                    entity_id=str(entity_item.id),
                    form_params=callback_data.form_params,
                    field_name=field_sequence[0],
                ).pack(),
            )
        )

    if (
        await check_entity_permission(
            entity=entity_item, user=user, permission=EntityPermission.DELETE_RLS
        )
        and form.show_delete_button
    ):
        edit_delete_row.append(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_DELETE_BTN)),
                callback_data=ContextData(
                    command=CallbackCommand.ENTITY_DELETE,
                    entity_name=entity_descriptor.name,
                    form_params=callback_data.form_params,
                    entity_id=str(entity_item.id),
                ).pack(),
            )
        )

    if edit_delete_row:
        keyboard_builder.row(*edit_delete_row)

    if form.item_repr:
        item_text = await get_callable_str(
            callable_str=form.item_repr,
            context=context,
            entity=entity_item,
        )
    else:
        item_text = await item_repr(entity_item=entity_item, context=context)

    context = pop_navigation_context(navigation_stack)
    if context:
        keyboard_builder.row(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_BACK_BTN)),
                callback_data=context.pack(),
            )
        )

    # state: FSMContext = kwargs["state"]
    # state_data = kwargs["state_data"]
    # await state.set_data(state_data)

    if query:
        send_message = get_send_message(query)
        await send_message(text=item_text, reply_markup=keyboard_builder.as_markup())
    else:
        await app.bot.send_message(
            chat_id=user.id,
            text=item_text,
            reply_markup=keyboard_builder.as_markup(),
        )


async def item_repr(entity_item: BotEntity, context: BotContext):
    entity_descriptor = entity_item.bot_entity_descriptor
    user = context.user
    entity_caption = (
        await get_callable_str(
            callable_str=entity_descriptor.full_name,
            context=context,
            descriptor=entity_descriptor,
        )
        if entity_descriptor.full_name
        else entity_descriptor.name
    )

    entity_item_repr = (
        await get_callable_str(
            callable_str=entity_descriptor.item_repr,
            context=context,
            entity=entity_item,
        )
        if entity_descriptor.item_repr
        else str(entity_item.id)
    )

    item_text = f"<b><u><i>{entity_caption or entity_descriptor.name}:</i></u></b> <b>{entity_item_repr}</b>"

    # user_permissions = get_user_permissions(user, entity_descriptor)

    for field_descriptor in entity_descriptor.fields_descriptors.values():
        if (
            isinstance(field_descriptor.is_visible, bool)
            and not field_descriptor.is_visible
        ):
            continue

        if callable(field_descriptor.is_visible):
            if iscoroutinefunction(field_descriptor.is_visible):
                field_visible = await field_descriptor.is_visible(
                    field_descriptor, entity_item, context
                )
            else:
                field_visible = field_descriptor.is_visible(
                    field_descriptor, entity_item, context
                )
            if not field_visible:
                continue

        if field_descriptor.caption_value:
            item_text += f"\n{
                await get_callable_str(
                    callable_str=field_descriptor.caption_value,
                    context=context,
                    descriptor=field_descriptor,
                    entity=entity_item,
                )
            }"
        else:
            field_caption = (
                await get_callable_str(
                    callable_str=field_descriptor.caption,
                    context=context,
                    descriptor=field_descriptor,
                )
                if field_descriptor.caption
                else field_descriptor.field_name
            )
            value = await get_value_repr(
                value=getattr(entity_item, field_descriptor.field_name),
                field_descriptor=field_descriptor,
                context=context,
                locale=user.lang,
            )
            item_text += f"\n{field_caption or field_descriptor.name}:{f' <b>{value}</b>' if value else ''}"
    return item_text
