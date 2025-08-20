from aiogram.filters.callback_data import CallbackData as BaseCallbackData
from enum import StrEnum


class CallbackCommand(StrEnum):
    FIELD_EDITOR = "fe"
    FIELD_EDITOR_CALLBACK = "fc"
    ENTITY_LIST = "el"
    ENTITY_ITEM = "ei"
    ENTITY_DELETE = "ed"
    MENU_ENTRY_MAIN = "mm"
    MENU_ENTRY_SETTINGS = "ms"
    MENU_ENTRY_ENTITIES = "me"
    MENU_ENTRY_PARAMETERS = "mp"
    MENU_ENTRY_LANGUAGE = "ml"
    SET_LANGUAGE = "ls"
    DATE_PICKER_MONTH = "dm"
    DATE_PICKER_YEAR = "dy"
    TIME_PICKER = "tp"
    ENTITY_PICKER_PAGE = "ep"
    ENTITY_PICKER_TOGGLE_ITEM = "et"
    VIEW_FILTER_EDIT = "vf"
    USER_COMMAND = "uc"
    DELETE_MESSAGE = "dl"


class CommandContext(StrEnum):
    SETTING_EDIT = "se"
    ENTITY_CREATE = "ec"
    ENTITY_EDIT = "ee"
    ENTITY_FIELD_EDIT = "ef"
    COMMAND_FORM = "cf"


class ContextData(BaseCallbackData, prefix="cd"):
    command: CallbackCommand
    context: CommandContext | None = None
    entity_name: str | None = None
    entity_id: int | None = None
    field_name: str | None = None
    form_params: str | None = None
    user_command: str | None = None
    data: str | None = None
    back: bool = False
