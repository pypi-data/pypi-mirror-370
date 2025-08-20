from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger

from ....model.settings import Settings
from ....model.user import UserBase
from ....utils.main import get_send_message
from ..context import ContextData, CallbackCommand
from ....auth import authorize_command
from ....utils.navigation import save_navigation_context, pop_navigation_context

logger = getLogger(__name__)
router = Router()


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.MENU_ENTRY_SETTINGS)
)
async def menu_entry_settings(message: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    stack = save_navigation_context(callback_data=callback_data, state_data=state_data)

    await settings_menu(message, navigation_stack=stack, **kwargs)


async def settings_menu(
    message: Message | CallbackQuery,
    user: UserBase,
    navigation_stack: list[ContextData],
    **kwargs,
):
    keyboard_builder = InlineKeyboardBuilder()

    if await authorize_command(
        user=user,
        callback_data=ContextData(command=CallbackCommand.MENU_ENTRY_PARAMETERS),
    ):
        keyboard_builder.row(
            InlineKeyboardButton(
                text=(await Settings.get(Settings.APP_STRINGS_PARAMETERS_BTN)),
                callback_data=ContextData(
                    command=CallbackCommand.MENU_ENTRY_PARAMETERS
                ).pack(),
            )
        )

    keyboard_builder.row(
        InlineKeyboardButton(
            text=(await Settings.get(Settings.APP_STRINGS_LANGUAGE_BTN)),
            callback_data=ContextData(
                command=CallbackCommand.MENU_ENTRY_LANGUAGE
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
        text=(await Settings.get(Settings.APP_STRINGS_SETTINGS)),
        reply_markup=keyboard_builder.as_markup(),
    )
