from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from .handlers.context import CallbackCommand, ContextData
from logging import getLogger


logger = getLogger(__name__)


class CallbackCommandFilter(Filter):
    def __init__(self, command: CallbackCommand):
        self.command = command

    async def __call__(self, *args, **kwargs):
        state: FSMContext = kwargs.get("state")
        state_data = await state.get_data()
        context_data = state_data.get("context_data")
        if context_data:
            try:
                context_data = ContextData.unpack(context_data)
            except Exception:
                logger.error("Error unpacking context data", exc_info=True)
                return False
            else:
                return context_data.command == self.command
        return False
