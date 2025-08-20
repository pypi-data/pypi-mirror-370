from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from babel.support import LazyProxy
from typing import Any, Awaitable, Callable, Dict

from ...model.user import UserBase


class AuthMiddleware(BaseMiddleware):
    def __init__[UserType: UserBase](
        self,
        user_class: type[UserType],
        not_authenticated_msg: LazyProxy | str = "not authenticated",
        not_active_msg: LazyProxy | str = "not active",
    ):
        self.user_class = user_class
        self.not_authenticated_msg = not_authenticated_msg
        self.not_active_msg = not_active_msg

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if event.business_connection_id:
            business_connection = await event.bot.get_business_connection(
                event.business_connection_id
            )
            user_id = business_connection.user.id
        else:
            user_id = event.from_user.id

        user = await self.user_class.get(id=user_id, session=data["db_session"])

        if user and user.is_active:
            data["user"] = user
            return await handler(event, data)

        if type(event) in [Message, CallbackQuery]:
            if user and not user.is_active:
                return await event.answer(self.not_active_msg)
            return await event.answer(self.not_authenticated_msg)
