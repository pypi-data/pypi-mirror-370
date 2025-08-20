"""
BotEntity module provides a metaclass and base class for creating database entities
with enhanced functionality for bot operations, including field descriptors,
filtering, and ownership management.
"""

from typing import (
    TYPE_CHECKING,
    dataclass_transform,
)
from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass
from sqlmodel import Field
from sqlmodel.main import FieldInfo


from .descriptors import EntityField, FieldDescriptor

if TYPE_CHECKING:
    pass


@dataclass_transform(
    kw_only_default=True,
    field_specifiers=(Field, FieldInfo, EntityField, FieldDescriptor),
)
class AnnotatedSchemaMetaclass(ModelMetaclass):
    """
    Metaclass for annotated schemas.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        """
        Create a new annotated schema.
        """

        # --- Create the class using parent metaclass ---
        type_ = super().__new__(mcs, name, bases, namespace, **kwargs)

        return type_


class AnnotatedSchema(BaseModel, metaclass=AnnotatedSchemaMetaclass):
    """
    Base class for annotated schemas.
    """
