from aiogram.types import InlineKeyboardButton

from ..utils.navigation import pop_navigation_context
from ..model.descriptors import CommandCallbackContext
from ..model.settings import Settings


async def get_back_button(
    context: CommandCallbackContext, text: str = None
) -> InlineKeyboardButton | None:
    stack = context.state_data.get("navigation_stack")
    if not stack:
        return None

    back_callback_data = pop_navigation_context(stack)

    if not text:
        text = await Settings.get(Settings.APP_STRINGS_BACK_BTN)

    return InlineKeyboardButton(
        text=text,
        callback_data=back_callback_data.pack(),
    )
