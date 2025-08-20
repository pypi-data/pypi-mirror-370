from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from logging import getLogger
from sqlmodel.ext.asyncio.session import AsyncSession

from ...main import QuickBot
from ...model.settings import Settings
from ...model.language import LanguageBase
from ...model.user import UserBase
from ...utils.main import clear_state


logger = getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start(message: Message, **kwargs):
    app: QuickBot = kwargs["app"]
    state: FSMContext = kwargs["state"]

    state_data = await state.get_data()
    clear_state(state_data=state_data, clear_nav=True)

    if app.start_handler:
        await app.start_handler(default_start_handler, message, **kwargs)
    else:
        await default_start_handler(message, **kwargs)

    await state.set_data(state_data)


async def default_start_handler[UserType: UserBase](
    message: Message,
    db_session: AsyncSession,
    app: QuickBot,
    state: FSMContext,
    **kwargs,
) -> tuple[UserType, bool]:
    User = app.user_class

    user = await User.get(session=db_session, id=message.from_user.id)

    if not user:
        is_new = True
        msg_text = (await Settings.get(Settings.APP_STRINGS_WELCOME_P_NAME)).format(
            name=message.from_user.full_name
        )

        try:
            if message.from_user.language_code in [
                item.value for item in LanguageBase.all_members.values()
            ]:
                lang = LanguageBase(message.from_user.language_code)
            else:
                lang = LanguageBase.EN

            user = await User.create(
                session=db_session,
                obj_in=User(
                    id=message.from_user.id,
                    name=message.from_user.full_name,
                    lang=lang,
                    is_active=True,
                ),
                commit=True,
            )

        except Exception as e:
            logger.error("Error creating user", exc_info=True)
            message.answer(
                (
                    await Settings.get(Settings.APP_STRINGS_INTERNAL_ERROR_P_ERROR)
                ).format(error=str(e))
            )

            return

    else:
        is_new = False
        if user.is_active:
            msg_text = (
                await Settings.get(Settings.APP_STRINGS_GREETING_P_NAME)
            ).format(name=user.name)
        else:
            msg_text = (
                await Settings.get(Settings.APP_STRINGS_USER_BLOCKED_P_NAME)
            ).format(name=user.name)

    await message.answer(msg_text)

    return user, is_new
