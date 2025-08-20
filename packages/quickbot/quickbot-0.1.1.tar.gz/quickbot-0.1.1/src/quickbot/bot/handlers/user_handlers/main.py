from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from typing import TYPE_CHECKING

from quickbot.utils.main import clear_state
from quickbot.utils.navigation import save_navigation_context

if TYPE_CHECKING:
    from quickbot.main import QuickBot

from ..context import ContextData, CallbackCommand
from .command_handler import command_handler

router = Router()


@router.message(F.text.startswith("/"))
async def command_text(message: Message, **kwargs):
    str_command = message.text.lstrip("/")
    callback_data = ContextData(
        command=CallbackCommand.USER_COMMAND, user_command=str_command
    )

    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    await process_command_handler(
        message=message, callback_data=callback_data, **kwargs
    )


@router.callback_query(ContextData.filter(F.command == CallbackCommand.USER_COMMAND))
async def command_callback(message: CallbackQuery, **kwargs):
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    await process_command_handler(message=message, **kwargs)


async def process_command_handler(message: Message | CallbackQuery, **kwargs):
    state_data: dict = kwargs["state_data"]
    callback_data: ContextData = kwargs["callback_data"]
    app: "QuickBot" = kwargs["app"]
    cmd = app.bot_commands.get(callback_data.user_command.split("&")[0])

    if cmd is None:
        return

    if cmd.clear_navigation:
        state_data.pop("navigation_stack", None)
        state_data.pop("navigation_context", None)

    if cmd.register_navigation:
        clear_state(state_data=state_data)
        save_navigation_context(callback_data=callback_data, state_data=state_data)

    await command_handler(message=message, cmd=cmd, **kwargs)
