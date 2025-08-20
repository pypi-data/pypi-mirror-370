from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from inspect import iscoroutinefunction
from typing import Any

from ....model.bot_entity import BotEntity
from ....model.bot_enum import BotEnum
from ....model.settings import Settings
from ....model.descriptors import BotContext, EntityForm, FieldDescriptor
from ....model.user import UserBase
from ..context import ContextData, CallbackCommand, CommandContext
from ....utils.navigation import get_navigation_context, pop_navigation_context
from ....utils.main import build_field_sequence, get_value_repr
from ....utils.serialization import serialize


async def wrap_editor(
    keyboard_builder: InlineKeyboardBuilder,
    field_descriptor: FieldDescriptor,
    callback_data: ContextData,
    state_data: dict,
    user: UserBase,
    context: BotContext,
    entity: BotEntity | Any = None,
):
    if callback_data.context in [
        CommandContext.ENTITY_CREATE,
        CommandContext.ENTITY_EDIT,
        CommandContext.ENTITY_FIELD_EDIT,
        CommandContext.COMMAND_FORM,
    ]:
        show_back = True
        show_cancel = True

        if callback_data.context == CommandContext.COMMAND_FORM:
            field_sequence = list(field_descriptor.command.param_form.keys())
            field_index = field_sequence.index(callback_data.field_name)
            show_back = field_descriptor.command.show_back_in_param_form
            show_cancel = field_descriptor.command.show_cancel_in_param_form
        else:
            form_name = (
                callback_data.form_params.split("&")[0]
                if callback_data.form_params
                else None
            )
            form: EntityForm = field_descriptor.entity_descriptor.forms.get(
                form_name, field_descriptor.entity_descriptor.default_form
            )
            if form.edit_field_sequence:
                field_sequence = form.edit_field_sequence
            else:
                field_sequence = await build_field_sequence(
                    entity_descriptor=field_descriptor.entity_descriptor,
                    user=user,
                    callback_data=callback_data,
                    state_data=state_data,
                    context=context,
                )
            field_index = (
                field_sequence.index(field_descriptor.name)
                if callback_data.context
                in [CommandContext.ENTITY_CREATE, CommandContext.ENTITY_EDIT]
                else 0
            )

        stack, navigation_context = get_navigation_context(state_data=state_data)
        navigation_context = pop_navigation_context(stack)

        if not issubclass(field_descriptor.type_base, BotEnum):
            options = []
            if field_descriptor.options:
                if isinstance(field_descriptor.options, list):
                    options = field_descriptor.options
                elif callable(field_descriptor.options):
                    if iscoroutinefunction(field_descriptor.options):
                        options = await field_descriptor.options(entity, context)
                    else:
                        options = field_descriptor.options(entity, context)

            for option_row in options:
                btns_row = []
                for option in option_row:
                    if isinstance(option, tuple):
                        value = option[0]
                        caption = option[1]
                    else:
                        value = option
                        caption = await get_value_repr(
                            value=value,
                            field_descriptor=field_descriptor,
                            context=context,
                        )

                    btns_row.append(
                        InlineKeyboardButton(
                            text=caption,
                            callback_data=ContextData(
                                command=CallbackCommand.FIELD_EDITOR_CALLBACK,
                                context=callback_data.context,
                                entity_name=callback_data.entity_name,
                                entity_id=callback_data.entity_id,
                                field_name=callback_data.field_name,
                                form_params=callback_data.form_params,
                                user_command=callback_data.user_command,
                                data=serialize(
                                    value=value,
                                    field_descriptor=field_descriptor,
                                ),
                            ).pack(),
                        )
                    )
                keyboard_builder.row(*btns_row)

        btns = []

        if field_index > 0 and show_back:
            btns.append(
                InlineKeyboardButton(
                    text=(await Settings.get(Settings.APP_STRINGS_BACK_BTN)),
                    callback_data=ContextData(
                        command=CallbackCommand.FIELD_EDITOR,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        field_name=field_sequence[field_index - 1],
                    ).pack(),
                )
            )

        if (
            field_descriptor.is_optional
            and field_descriptor.show_skip_in_editor == "Auto"
        ):
            btns.append(
                InlineKeyboardButton(
                    text=(await Settings.get(Settings.APP_STRINGS_SKIP_BTN)),
                    callback_data=ContextData(
                        command=CallbackCommand.FIELD_EDITOR_CALLBACK,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data="skip",
                    ).pack(),
                )
            )

        keyboard_builder.row(*btns)

        if show_cancel:
            keyboard_builder.row(
                InlineKeyboardButton(
                    text=(await Settings.get(Settings.APP_STRINGS_CANCEL_BTN)),
                    callback_data=navigation_context.pack()
                    if navigation_context
                    else ContextData(
                        command=CallbackCommand.DELETE_MESSAGE, data="clear_nav"
                    ).pack(),
                )
            )

    elif callback_data.context == CommandContext.SETTING_EDIT:
        keyboard_builder.row(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_CANCEL_BTN)),
                callback_data=ContextData(
                    command=CallbackCommand.FIELD_EDITOR_CALLBACK,
                    context=callback_data.context,
                    field_name=callback_data.field_name,
                    form_params=callback_data.form_params,
                    data="cancel",
                ).pack(),
            )
        )
