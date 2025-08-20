from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger
from typing import Any

from ....model.descriptors import BotContext, FieldDescriptor
from ....model.language import LanguageBase
from ....model.settings import Settings
from ....model.user import UserBase
from ....utils.main import get_send_message, get_local_text
from ....utils.serialization import serialize
from ..context import ContextData, CallbackCommand
from .wrapper import wrap_editor


logger = getLogger(__name__)
router = Router()


async def string_editor(
    message: Message | CallbackQuery,
    field_descriptor: FieldDescriptor,
    callback_data: ContextData,
    current_value: Any,
    edit_prompt: str,
    state: FSMContext,
    user: UserBase,
    locale_index: int = 0,
    **kwargs,
):
    keyboard_builder = InlineKeyboardBuilder()

    state_data: dict = kwargs["state_data"]

    _edit_prompt = edit_prompt

    context_data = ContextData(
        command=CallbackCommand.FIELD_EDITOR_CALLBACK,
        context=callback_data.context,
        entity_name=callback_data.entity_name,
        entity_id=callback_data.entity_id,
        field_name=callback_data.field_name,
        form_params=callback_data.form_params,
        user_command=callback_data.user_command,
    )

    if field_descriptor.type_base is str and field_descriptor.localizable:
        current_locale = list(LanguageBase.all_members.values())[locale_index]

        _edit_prompt = f"{edit_prompt}\n{
            (
                await Settings.get(
                    Settings.APP_STRINGS_STRING_EDITOR_LOCALE_TEMPLATE_P_NAME
                )
            ).format(name=current_locale)
        }"
        _current_value = (
            get_local_text(current_value, current_locale) if current_value else None
        )

        state_data.update(
            {
                "context_data": context_data.pack(),
                "edit_prompt": edit_prompt,
                "locale_index": str(locale_index),
                "current_value": current_value,
            }
        )

    else:
        _current_value = serialize(current_value, field_descriptor)

        state_data.update({"context_data": context_data.pack()})

    if (
        _current_value
        and field_descriptor.show_current_value_button
        and field_descriptor.options_custom_value
    ):
        _current_value_caption = (
            f"{_current_value[:30]}..." if len(_current_value) > 30 else _current_value
        )
        keyboard_builder.row(
            InlineKeyboardButton(
                text=_current_value_caption,
                copy_text=CopyTextButton(text=_current_value[:256]),
            )
        )

    state_data = kwargs["state_data"]

    context = BotContext(
        db_session=kwargs["db_session"],
        app=kwargs["app"],
        app_state=kwargs["app_state"],
        user=user,
        message=message,
    )

    await wrap_editor(
        keyboard_builder=keyboard_builder,
        field_descriptor=field_descriptor,
        callback_data=callback_data,
        state_data=state_data,
        user=user,
        context=context,
        entity=kwargs.get("entity_data"),
    )

    await state.set_data(state_data)

    send_message = get_send_message(message)
    await send_message(text=_edit_prompt, reply_markup=keyboard_builder.as_markup())
