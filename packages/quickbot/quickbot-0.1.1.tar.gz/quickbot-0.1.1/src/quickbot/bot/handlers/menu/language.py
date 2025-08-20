from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import I18n
from logging import getLogger
from sqlmodel.ext.asyncio.session import AsyncSession

from ....utils.navigation import pop_navigation_context, save_navigation_context
from ....model.language import LanguageBase
from ....model.settings import Settings
from ....model.user import UserBase
from ..context import ContextData, CallbackCommand
from ....utils.main import get_send_message


logger = getLogger(__name__)
router = Router()


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.MENU_ENTRY_LANGUAGE)
)
async def menu_entry_language(message: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    stack = save_navigation_context(callback_data=callback_data, state_data=state_data)

    await language_menu(message, navigation_stack=stack, **kwargs)


async def language_menu(
    message: Message | CallbackQuery,
    navigation_stack: list[ContextData],
    user: UserBase,
    **kwargs,
):
    send_message = get_send_message(message)

    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=locale.localized(user.lang.value),
                callback_data=ContextData(
                    command=CallbackCommand.SET_LANGUAGE, data=str(locale)
                ).pack(),
            )
        ]
        for locale in LanguageBase.all_members.values()
    ]

    context = pop_navigation_context(navigation_stack)
    if context:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=(await Settings.get(Settings.APP_STRINGS_BACK_BTN)),
                    callback_data=context.pack(),
                )
            ]
        )

    state: FSMContext = kwargs["state"]
    state_data = kwargs["state_data"]
    await state.set_data(state_data)

    await send_message(
        text=(await Settings.get(Settings.APP_STRINGS_LANGUAGE)),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard),
    )


@router.callback_query(ContextData.filter(F.command == CallbackCommand.SET_LANGUAGE))
async def set_language(message: CallbackQuery, **kwargs):
    user: UserBase = kwargs["user"]
    callback_data: ContextData = kwargs["callback_data"]
    db_session: AsyncSession = kwargs["db_session"]
    state: FSMContext = kwargs["state"]

    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    user.lang = LanguageBase(callback_data.data)
    await db_session.commit()

    i18n: I18n = kwargs["i18n"]
    with i18n.use_locale(user.lang.value):
        await route_callback(message, **kwargs)


from ..common.routing import route_callback  # noqa: E402
