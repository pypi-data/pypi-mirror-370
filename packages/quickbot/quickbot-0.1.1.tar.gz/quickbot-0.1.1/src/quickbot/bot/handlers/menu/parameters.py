from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger

from quickbot.model.descriptors import BotContext

from ....model.settings import Settings
from ....model.user import UserBase
from ..context import ContextData, CallbackCommand, CommandContext
from ....utils.main import (
    get_send_message,
    clear_state,
    get_value_repr,
    get_callable_str,
)
from ....utils.navigation import save_navigation_context, pop_navigation_context
from ....auth import authorize_command


logger = getLogger(__name__)
router = Router()


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.MENU_ENTRY_PARAMETERS)
)
async def menu_entry_parameters(message: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    clear_state(state_data=state_data)
    stack = save_navigation_context(callback_data=callback_data, state_data=state_data)

    await parameters_menu(message=message, navigation_stack=stack, **kwargs)


async def parameters_menu(
    message: Message | CallbackQuery,
    user: UserBase,
    callback_data: ContextData,
    navigation_stack: list[ContextData],
    **kwargs,
):
    if not await authorize_command(user=user, callback_data=callback_data):
        await message.answer(await Settings.get(Settings.APP_STRINGS_FORBIDDEN))

    settings = await Settings.get_params()

    keyboard_builder = InlineKeyboardBuilder()
    for key, value in settings.items():
        if not key.is_visible:
            continue

        context = BotContext(
            db_session=kwargs["db_session"],
            app=kwargs["app"],
            app_state=kwargs["app_state"],
            user=user,
            message=message,
        )

        if key.caption_value:
            caption = await get_callable_str(
                callable_str=key.caption_value,
                context=context,
                descriptor=key,
                entity={key.field_name: value},
            )
        else:
            if key.caption:
                caption = await get_callable_str(
                    callable_str=key.caption,
                    context=context,
                    descriptor=key,
                )
            else:
                caption = key.name

            if key.type_ is bool:
                caption = f"{'[✓]' if value else '[  ]'} {caption}"
            else:
                caption = f"{caption}: {await get_value_repr(value=value, field_descriptor=key, context=context, locale=user.lang)}"

        keyboard_builder.row(
            InlineKeyboardButton(
                text=caption,
                callback_data=ContextData(
                    command=CallbackCommand.FIELD_EDITOR,
                    context=CommandContext.SETTING_EDIT,
                    field_name=key.name,
                ).pack(),
            )
        )

    context = pop_navigation_context(navigation_stack)
    if context:
        keyboard_builder.row(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_BACK_BTN)),
                callback_data=context.pack(),
            )
        )

    state: FSMContext = kwargs["state"]
    state_data = kwargs["state_data"]
    await state.set_data(state_data)

    send_message = get_send_message(message)

    await send_message(
        text=(await Settings.get(Settings.APP_STRINGS_PARAMETERS)),
        reply_markup=keyboard_builder.as_markup(),
    )
