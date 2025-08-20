from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger
from typing import TYPE_CHECKING

from quickbot.model.descriptors import BotContext
from ....model.settings import Settings
from ..context import ContextData, CallbackCommand
from ....utils.main import get_send_message, get_callable_str
from ....utils.navigation import save_navigation_context, pop_navigation_context

if TYPE_CHECKING:
    from ....main import QuickBot


logger = getLogger(__name__)
router = Router()


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.MENU_ENTRY_ENTITIES)
)
async def menu_entry_entities(message: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    stack = save_navigation_context(callback_data=callback_data, state_data=state_data)

    await entities_menu(message=message, navigation_stack=stack, **kwargs)


async def entities_menu(
    message: Message | CallbackQuery,
    app: "QuickBot",
    state: FSMContext,
    navigation_stack: list[ContextData],
    **kwargs,
):
    keyboard_builder = InlineKeyboardBuilder()

    entity_metadata = app.bot_metadata

    for entity in entity_metadata.entity_descriptors.values():
        if entity.show_in_entities_menu:
            if entity.full_name_plural:
                caption = await get_callable_str(
                    callable_str=entity.full_name_plural,
                    context=BotContext(
                        db_session=kwargs["db_session"],
                        app=app,
                        app_state=kwargs["app_state"],
                        user=kwargs["user"],
                        message=message,
                    ),
                    descriptor=entity,
                )
            else:
                caption = entity.name

            caption = f"{f'{entity.icon} ' if entity.icon else ''}{caption}"

            keyboard_builder.row(
                InlineKeyboardButton(
                    text=caption,
                    callback_data=ContextData(
                        command=CallbackCommand.ENTITY_LIST, entity_name=entity.name
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

    state_data = kwargs["state_data"]
    await state.set_data(state_data)

    send_message = get_send_message(message)

    await send_message(
        text=(await Settings.get(Settings.APP_STRINGS_REFERENCES)),
        reply_markup=keyboard_builder.as_markup(),
    )
