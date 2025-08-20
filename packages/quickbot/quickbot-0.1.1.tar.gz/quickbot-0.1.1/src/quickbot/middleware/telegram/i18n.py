from typing import Optional, Dict, Any
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from aiogram.types import TelegramObject
from ...model.user import UserBase


class I18nMiddleware(SimpleI18nMiddleware):
    def __init__[UserType: UserBase](
        self,
        user_class: type[UserType],
        i18n: I18n,
        i18n_key: Optional[str] = "i18n",
        middleware_key: str = "i18n_middleware",
    ) -> None:
        self.user_class = user_class
        super().__init__(i18n=i18n, i18n_key=i18n_key, middleware_key=middleware_key)

    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        db_session = data.get("db_session")
        if db_session and event.__dict__.get("from_user"):
            user = await self.user_class.get(id=event.from_user.id, session=db_session)
            if user and user.lang:
                return user.lang.value
        return await super().get_locale(event=event, data=data)
