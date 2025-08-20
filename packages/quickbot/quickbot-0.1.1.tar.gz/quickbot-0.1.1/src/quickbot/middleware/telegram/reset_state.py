# from typing import Any, Awaitable, Callable, Dict
# from aiogram import BaseMiddleware
# from aiogram.types import TelegramObject
# from aiogram.fsm.context import FSMContext
# from aiogram.utils.i18n import gettext as _

# from ...bot.handlers.context import ContextData


# class ResetStateMiddleware(BaseMiddleware):
#     async def __call__(self,
#                        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#                        event: TelegramObject,
#                        data: Dict[str, Any]) -> Any:

#         save_state = False
#         callback_data = data.get("callback_data")
#         if isinstance(callback_data, ContextData):
#             save_state = callback_data.save_state

#         if not save_state:
#             state = data.get("state")
#             if isinstance(state, FSMContext):
#                 await state.clear()

#         return await handler(event, data)
