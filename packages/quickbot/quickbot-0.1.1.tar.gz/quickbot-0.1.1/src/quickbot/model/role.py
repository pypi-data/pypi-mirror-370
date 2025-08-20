from .bot_enum import BotEnum, EnumMember


class RoleBase(BotEnum):
    SUPER_USER = EnumMember("super_user")
    DEFAULT_USER = EnumMember("default_user")
