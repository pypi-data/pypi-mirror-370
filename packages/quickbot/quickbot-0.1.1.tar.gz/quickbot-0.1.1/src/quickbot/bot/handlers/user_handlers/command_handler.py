from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING

from quickbot.utils.main import clear_state
from quickbot.utils.navigation import (
    get_navigation_context,
    pop_navigation_context,
)
from quickbot.bot.handlers.editors.main import field_editor
from quickbot.utils.serialization import deserialize
from quickbot.utils.main import get_send_message
from quickbot.model.descriptors import BotCommand, CommandCallbackContext
from quickbot.model.settings import Settings

if TYPE_CHECKING:
    from quickbot.main import QuickBot
    from quickbot.model.user import UserBase

from ..context import ContextData, CallbackCommand, CommandContext


async def command_handler(message: Message | CallbackQuery, cmd: BotCommand, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    state: FSMContext = kwargs["state"]
    state_data: dict = kwargs["state_data"]
    app: "QuickBot" = kwargs["app"]
    user: "UserBase" = kwargs["user"]

    entity_data_dict: dict = state_data.get("entity_data")
    form_data = (
        {
            key: await deserialize(
                session=kwargs["db_session"],
                type_=cmd.param_form[key].type_,
                value=value,
            )
            for key, value in entity_data_dict.items()
        }
        if entity_data_dict and cmd.param_form
        else None
    )

    callback_context = CommandCallbackContext(
        message=message,
        callback_data=callback_data,
        form_data=form_data,
        db_session=kwargs["db_session"],
        user=user,
        app=app,
        app_state=kwargs["app_state"],
        state_data=state_data,
        state=state,
        i18n=kwargs["i18n"],
        register_navigation=cmd.register_navigation,
        clear_navigation=cmd.clear_navigation,
        kwargs=kwargs,
    )

    if cmd.pre_check and (not cmd.param_form or (cmd.param_form and form_data is None)):
        if iscoroutinefunction(cmd.pre_check):
            if not await cmd.pre_check(callback_context):
                return
        else:
            if not cmd.pre_check(callback_context):
                return

    if form_data is None and cmd.param_form:
        field_descriptor = list(cmd.param_form.values())[0]
        kwargs["callback_data"] = ContextData(
            command=CallbackCommand.FIELD_EDITOR,
            context=CommandContext.COMMAND_FORM,
            field_name=field_descriptor.name,
            user_command=callback_data.user_command,
        )

        return await field_editor(message=message, **kwargs)

    await cmd.handler(callback_context)

    if callback_context.register_navigation:
        await state.set_data(state_data)

        stack, navigation_context = get_navigation_context(state_data=state_data)
        back_callback_data = pop_navigation_context(stack=stack)
        if back_callback_data:
            callback_context.keyboard_builder.row(
                InlineKeyboardButton(
                    text=(await Settings.get(Settings.APP_STRINGS_BACK_BTN)),
                    callback_data=back_callback_data.pack(),
                )
            )
    if message:
        send_message = get_send_message(message)

        if callback_context.message_text:
            await send_message(
                text=callback_context.message_text,
                reply_markup=callback_context.keyboard_builder.as_markup(),
            )
        elif isinstance(message, CallbackQuery):
            await message.message.edit_reply_markup(
                reply_markup=callback_context.keyboard_builder.as_markup()
            )
    else:
        if callback_context.message_text:
            await app.bot.send_message(
                chat_id=user.id,
                text=callback_context.message_text,
                reply_markup=callback_context.keyboard_builder.as_markup(),
            )

    if not callback_context.register_navigation:
        if callback_context.clear_navigation:
            clear_state(state_data=state_data, clear_nav=True)
            await state.set_data(state_data)
        else:
            clear_state(state_data=state_data)
            await route_callback(message, back=True, **kwargs)


from quickbot.bot.handlers.common.routing import route_callback  # noqa: E402
