from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickbot.main import QuickBot

from ..context import CallbackCommand

from ....utils.navigation import (
    get_navigation_context,
    save_navigation_context,
    pop_navigation_context,
)


async def route_callback(message: Message | CallbackQuery, back: bool = True, **kwargs):
    import quickbot.bot.handlers.menu.main as menu_main
    import quickbot.bot.handlers.menu.language as menu_language
    import quickbot.bot.handlers.menu.settings as menu_settings
    import quickbot.bot.handlers.menu.parameters as menu_parameters
    import quickbot.bot.handlers.menu.entities as menu_entities
    import quickbot.bot.handlers.forms.entity_list as form_list
    import quickbot.bot.handlers.forms.entity_form as form_item
    import quickbot.bot.handlers.editors.main as editor
    import quickbot.bot.handlers.user_handlers.main as user_handler

    state_data = kwargs["state_data"]
    state: FSMContext = kwargs["state"]
    stack, context = get_navigation_context(state_data)
    if back:
        context = pop_navigation_context(stack)
        stack = save_navigation_context(callback_data=context, state_data=state_data)
    kwargs.update({"callback_data": context, "navigation_stack": stack})
    await state.set_data(state_data)
    if context:
        if context.command == CallbackCommand.MENU_ENTRY_MAIN:
            await menu_main.main_menu(message, **kwargs)
        elif context.command == CallbackCommand.MENU_ENTRY_SETTINGS:
            await menu_settings.settings_menu(message, **kwargs)
        elif context.command == CallbackCommand.MENU_ENTRY_PARAMETERS:
            await menu_parameters.parameters_menu(message, **kwargs)
        elif context.command == CallbackCommand.MENU_ENTRY_LANGUAGE:
            await menu_language.language_menu(message, **kwargs)
        elif context.command == CallbackCommand.MENU_ENTRY_ENTITIES:
            await menu_entities.entities_menu(message, **kwargs)
        elif context.command == CallbackCommand.ENTITY_LIST:
            await form_list.entity_list(message, **kwargs)
        elif context.command == CallbackCommand.ENTITY_ITEM:
            await form_item.entity_item(message, **kwargs)
        elif context.command == CallbackCommand.FIELD_EDITOR:
            await editor.field_editor(message, **kwargs)
        elif context.command == CallbackCommand.USER_COMMAND:
            app: "QuickBot" = kwargs["app"]
            cmd = app.bot_commands.get(context.user_command.split("&")[0])

            await user_handler.command_handler(message=message, cmd=cmd, **kwargs)
        else:
            raise ValueError(f"Unknown command {context.command}")
    else:
        raise ValueError("No navigation context")
