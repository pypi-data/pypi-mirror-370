from typing import Any, Type
from pydantic import BaseModel
from sqlmodel import TypeDecorator, JSON


class PydanticJSON(TypeDecorator):
    """
    SQLAlchemy-compatible JSON type for storing Pydantic models
    (including nested ones). Automatically serializes on insert
    and deserializes on read.
    """

    impl = JSON
    cache_ok = True

    def __init__(self, model_class: Type[BaseModel], *args, **kwargs):
        if not issubclass(model_class, BaseModel):
            raise TypeError("PydanticJSON expects a Pydantic BaseModel subclass")
        self.model_class = model_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value: Any, dialect) -> Any:
        """
        Serialize Python object to JSON-compatible form before saving to DB.
        """
        if value is None:
            return None

        if isinstance(value, list):
            return [
                item.model_dump(mode="json") if isinstance(item, BaseModel) else item
                for item in value
            ]

        if isinstance(value, BaseModel):
            return value.model_dump(mode="json")

        return value  # assume already JSON-serializable

    def process_result_value(self, value: Any, dialect) -> Any:
        """
        Deserialize JSON data from DB back into Python object.
        """
        if value is None:
            return None

        if isinstance(value, list):
            return [self.model_class(**item) for item in value]

        if isinstance(value, dict):
            return self.model_class(**value)

        raise TypeError(f"Unsupported value type for deserialization: {type(value)}")
