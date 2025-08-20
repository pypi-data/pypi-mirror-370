from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger
from ....model.settings import Settings
from ..context import ContextData, CallbackCommand
from ....utils.main import get_send_message
from ....utils.navigation import save_navigation_context, pop_navigation_context

import quickbot.bot.handlers.menu.entities as entities
import quickbot.bot.handlers.menu.settings as settings
import quickbot.bot.handlers.menu.parameters as parameters
import quickbot.bot.handlers.menu.language as language
import quickbot.bot.handlers.editors.main as editor
import quickbot.bot.handlers.editors.main_callbacks as editor_callbacks
import quickbot.bot.handlers.forms.entity_list as entity_list
import quickbot.bot.handlers.forms.entity_form as entity_form
import quickbot.bot.handlers.forms.entity_form_callbacks as entity_form_callbacks
import quickbot.bot.handlers.common.filtering_callbacks as filtering_callbacks
import quickbot.bot.handlers.user_handlers.main as user_handlers_main


logger = getLogger(__name__)
router = Router()


@router.callback_query(ContextData.filter(F.command == CallbackCommand.MENU_ENTRY_MAIN))
async def menu_entry_main(message: CallbackQuery, **kwargs):
    stack = save_navigation_context(
        callback_data=kwargs["callback_data"], state=kwargs["state"]
    )

    await main_menu(message, navigation_stack=stack, **kwargs)


async def main_menu(
    message: Message | CallbackQuery, navigation_stack: list[ContextData], **kwargs
):
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.row(
        InlineKeyboardButton(
            text=(await Settings.get(Settings.APP_STRINGS_REFERENCES_BTN)),
            callback_data=ContextData(
                command=CallbackCommand.MENU_ENTRY_ENTITIES
            ).pack(),
        )
    )

    keyboard_builder.row(
        InlineKeyboardButton(
            text=(await Settings.get(Settings.APP_STRINGS_SETTINGS_BTN)),
            callback_data=ContextData(
                command=CallbackCommand.MENU_ENTRY_SETTINGS
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

    send_message = get_send_message(message)

    await send_message(
        text=(await Settings.get(Settings.APP_STRINGS_MAIN_NENU)),
        reply_markup=keyboard_builder.as_markup(),
    )


router.include_routers(
    entities.router,
    settings.router,
    parameters.router,
    language.router,
    editor.router,
    editor_callbacks.router,
    entity_list.router,
    entity_form.router,
    entity_form_callbacks.router,
    filtering_callbacks.router,
    user_handlers_main.router,
)
