from ..model.settings import Settings
from ..model.user import UserBase
from ..bot.handlers.context import ContextData, CallbackCommand, CommandContext


async def authorize_command(user: UserBase, callback_data: ContextData):
    if (
        callback_data.command == CallbackCommand.MENU_ENTRY_PARAMETERS
        or callback_data.context == CommandContext.SETTING_EDIT
    ):
        allowed_roles = await Settings.get(Settings.SECURITY_PARAMETERS_ROLES)
        return any(role in user.roles for role in allowed_roles)

    return False
