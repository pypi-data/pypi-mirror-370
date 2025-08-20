from enum import StrEnum


class CrudCommand(StrEnum):
    LIST = "list"
    GET_BY_ID = "get_by_id"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
