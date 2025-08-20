from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from babel.support import LazyProxy
from logging import getLogger

from ....model.descriptors import BotContext, FieldDescriptor
from ....model.user import UserBase
from ..context import ContextData, CallbackCommand
from ....utils.main import get_send_message
from .wrapper import wrap_editor


logger = getLogger(__name__)
router = Router()


async def bool_editor(
    message: Message | CallbackQuery,
    edit_prompt: str,
    field_descriptor: FieldDescriptor,
    callback_data: ContextData,
    user: UserBase,
    **kwargs,
):
    keyboard_builder = InlineKeyboardBuilder()

    if isinstance(field_descriptor.bool_true_value, LazyProxy):
        true_caption = field_descriptor.bool_true_value.value
    else:
        true_caption = field_descriptor.bool_true_value

    if isinstance(field_descriptor.bool_false_value, LazyProxy):
        false_caption = field_descriptor.bool_false_value.value
    else:
        false_caption = field_descriptor.bool_false_value

    keyboard_builder.row(
        InlineKeyboardButton(
            text=true_caption,
            callback_data=ContextData(
                command=CallbackCommand.FIELD_EDITOR_CALLBACK,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=str(True),
            ).pack(),
        ),
        InlineKeyboardButton(
            text=false_caption,
            callback_data=ContextData(
                command=CallbackCommand.FIELD_EDITOR_CALLBACK,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=str(False),
            ).pack(),
        ),
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
    )

    state: FSMContext = kwargs["state"]
    await state.set_data(state_data)

    send_message = get_send_message(message)

    await send_message(text=edit_prompt, reply_markup=keyboard_builder.as_markup())
