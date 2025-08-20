from inspect import iscoroutinefunction
from typing import Any, Optional, get_origin
from pydantic import BaseModel, Field
from pydantic.fields import _Unset
from pydantic_core import PydanticUndefined
from typing_extensions import Literal
from sqlmodel import SQLModel, col, column
from sqlmodel.sql.expression import SelectOfScalar
from typing import TYPE_CHECKING

from quickbot.model.list_schema import ListSchema
from quickbot.model.descriptors import (
    EntityDescriptor,
    Filter,
    FilterExpression,
    BotContext,
)
from quickbot.utils.main import get_entity_item_repr

if TYPE_CHECKING:
    from quickbot import BotEntity, BotEnum
    from quickbot.model.user import UserBase


def entity_to_schema(entity: "BotEntity") -> BaseModel:
    entity_data = {}
    for field_descriptor in entity.bot_entity_descriptor.fields_descriptors.values():
        if field_descriptor.is_list and is_bot_entity(field_descriptor.type_base):
            entity_data[field_descriptor.field_name] = [
                item.id for item in getattr(entity, field_descriptor.field_name)
            ]
        elif field_descriptor.is_list and is_bot_enum(field_descriptor.type_base):
            entity_data[field_descriptor.field_name] = [
                item.value for item in getattr(entity, field_descriptor.field_name)
            ]
        elif not field_descriptor.is_list and is_bot_entity(field_descriptor.type_base):
            continue
        elif not field_descriptor.is_list and is_bot_enum(field_descriptor.type_base):
            val: "BotEnum" | None = getattr(entity, field_descriptor.field_name)
            entity_data[field_descriptor.field_name] = val.value if val else None
        else:
            entity_data[field_descriptor.field_name] = getattr(
                entity, field_descriptor.field_name
            )
    return (
        entity.bot_entity_descriptor.crud.schema(**entity_data)
        if entity.bot_entity_descriptor.crud
        else entity.bot_entity_descriptor.schema(**entity_data)
    )


async def entity_to_list_schema(
    entity: "BotEntity", context: "BotContext"
) -> ListSchema:
    entity_repr = await get_entity_item_repr(
        entity, context, entity.bot_entity_descriptor.item_repr
    )
    return ListSchema(id=entity.id, name=entity_repr)


def _pydantic_model_fields(
    namespace: dict[str, Any],
    entity_descriptor: EntityDescriptor,
    schema_type: Literal["schema", "create", "update"] = "schema",
) -> dict[str, Any]:
    namespace["__annotations__"] = {}
    for field_descriptor in entity_descriptor.fields_descriptors.values():
        type_origin = get_origin(field_descriptor.type_base)
        if (
            type_origin is not list
            and not field_descriptor.is_list
            and (
                issubclass(field_descriptor.type_base, SQLModel)
                or isinstance(field_descriptor.type_base, str)
            )
        ) or (
            schema_type in ["create", "update"]
            and field_descriptor.field_name == "id"
            and field_descriptor.default is None
        ):
            continue

        if (
            type_origin is not list
            and field_descriptor.is_list
            and (
                issubclass(field_descriptor.type_base, SQLModel)
                or isinstance(field_descriptor.type_base, str)
            )
        ):
            namespace["__annotations__"][field_descriptor.field_name] = list[int]
        elif type_origin is not list and is_bot_enum(field_descriptor.type_base):
            enum_values = [
                member.value
                for member in field_descriptor.type_base.all_members.values()
            ]
            enum_annotation = (
                list[Literal[*enum_values]]
                if field_descriptor.is_list
                else Literal[*enum_values]
            )
            if field_descriptor.is_optional:
                enum_annotation = Optional[enum_annotation]
            namespace["__annotations__"][field_descriptor.field_name] = enum_annotation
        else:
            namespace["__annotations__"][field_descriptor.field_name] = (
                Optional[field_descriptor.type_base]
                if field_descriptor.is_optional
                else field_descriptor.type_
            )

        description = (
            field_descriptor.description if field_descriptor.description else _Unset
        )

        if schema_type == "schema" and field_descriptor.is_optional:
            namespace[field_descriptor.field_name] = Field(description=description)
        elif schema_type == "create":
            if field_descriptor.default is not PydanticUndefined:
                namespace[field_descriptor.field_name] = Field(
                    default=field_descriptor.default, description=description
                )
            elif field_descriptor.default_factory is not None:
                namespace[field_descriptor.field_name] = Field(
                    default_factory=field_descriptor.default_factory,
                    description=description,
                )
            elif field_descriptor.is_optional:
                namespace[field_descriptor.field_name] = Field(
                    default=None, description=description
                )
            else:
                namespace[field_descriptor.field_name] = Field(description=description)
        elif schema_type == "update":
            namespace[field_descriptor.field_name] = Field(
                default=None, description=description
            )
        else:
            namespace[field_descriptor.field_name] = Field(description=description)


def pydantic_model(
    entity_descriptor: EntityDescriptor,
    module_name: str,
    schema_type: Literal["schema", "create", "update"] = "schema",
) -> type[BaseModel]:
    namespace = {
        "__module__": module_name,
    }
    _pydantic_model_fields(namespace, entity_descriptor, schema_type)

    return type(
        f"{entity_descriptor.class_name}{schema_type.capitalize() if schema_type != 'schema' else ''}Schema",
        (BaseModel,),
        namespace,
    )


def _build_filter_condition(
    cls: type["BotEntity"], filter_obj: Filter | FilterExpression
) -> Any:
    """
    Build SQLAlchemy condition from a Filter or FilterExpression object.

    Args:
        filter_obj: Filter or FilterExpression object to convert

    Returns:
        SQLAlchemy condition
    """
    # --- Handle single Filter object ---
    if isinstance(filter_obj, Filter):
        # Support both string field names and callables for custom columns
        if isinstance(filter_obj.field, str):
            column = getattr(cls, filter_obj.field)
        else:
            column = filter_obj.field(cls)
        # Map filter operator to SQLAlchemy expression
        if filter_obj.operator == "==":
            return column.__eq__(filter_obj.value)
        elif filter_obj.operator == "!=":
            return column.__ne__(filter_obj.value)
        elif filter_obj.operator == "<":
            return column.__lt__(filter_obj.value)
        elif filter_obj.operator == "<=":
            return column.__le__(filter_obj.value)
        elif filter_obj.operator == ">":
            return column.__gt__(filter_obj.value)
        elif filter_obj.operator == ">=":
            return column.__ge__(filter_obj.value)
        elif filter_obj.operator == "ilike":
            return col(column).ilike(f"%{filter_obj.value}%")
        elif filter_obj.operator == "like":
            return col(column).like(f"%{filter_obj.value}%")
        elif filter_obj.operator == "in":
            return col(column).in_(filter_obj.value)
        elif filter_obj.operator == "not in":
            return col(column).notin_(filter_obj.value)
        elif filter_obj.operator == "is none":
            return col(column).is_(None)
        elif filter_obj.operator == "is not none":
            return col(column).isnot(None)
        elif filter_obj.operator == "contains":
            return filter_obj.value == col(column).any_()
        else:
            # Unknown operator, return None (no condition)
            return None
    # --- Handle FilterExpression object (logical AND/OR of filters) ---
    elif isinstance(filter_obj, FilterExpression):
        operator = filter_obj.operator
        filters = filter_obj.filters
        # Recursively build conditions for all sub-filters
        conditions = []
        for sub_filter in filters:
            condition = _build_filter_condition(cls, sub_filter)
            if condition is not None:
                conditions.append(condition)
        if not conditions:
            return None
        # Combine conditions using logical AND/OR
        if operator == "and":
            res_condition = conditions[0]
            if len(conditions) > 1:
                for condition in conditions[1:]:
                    res_condition = res_condition & condition
            return res_condition
        elif operator == "or":
            res_condition = conditions[0]
            if len(conditions) > 1:
                for condition in conditions[1:]:
                    res_condition = res_condition | condition
            return res_condition


def _static_filter_condition(
    cls,
    select_statement: SelectOfScalar,
    static_filter: Filter | FilterExpression,
):
    """
    Apply static filters to a select statement.

    Static filters are predefined conditions that don't depend on user input.
    Supports both Filter and FilterExpression objects with logical operations.

    Args:
        select_statement: SQLAlchemy select statement to modify
        static_filter: filter condition to apply

    Returns:
        Modified select statement with filter conditions
    """
    condition = _build_filter_condition(cls, static_filter)
    if condition is not None:
        select_statement = select_statement.where(condition)
    return select_statement


def _filter_condition(
    select_statement: SelectOfScalar,
    filter: str,
    filter_fields: list[str],
):
    """
    Apply text-based search filters to a select statement.

    Creates a case-insensitive LIKE search across multiple fields.

    Args:
        select_statement: SQLAlchemy select statement to modify
        filter: Search text to look for
        filter_fields: List of field names to search in

    Returns:
        Modified select statement with search conditions
    """
    condition = None
    for field in filter_fields:
        if condition is not None:
            condition = condition | (column(field).ilike(f"%{filter}%"))
        else:
            condition = column(field).ilike(f"%{filter}%")
    return select_statement.where(condition)


async def _apply_rls_filters(
    cls: type["BotEntity"], select_statement: SelectOfScalar, user: "UserBase"
):
    """
    Apply Row Level Security (RLS) filters to restrict access based on user roles.

    This method uses the entity's rls_filters and rls_filters_params to apply
    dynamic filtering conditions based on the user's roles and permissions.

    Args:
        select_statement: SQLAlchemy select statement to modify
        user: User whose access should be restricted

    Returns:
        Modified select statement with RLS conditions
    """
    # --- Check if RLS filters are defined for this entity ---
    if cls.bot_entity_descriptor.rls_filters:
        # Get parameters for RLS filters (may be sync or async)
        params = []
        if cls.bot_entity_descriptor.rls_filters_params:
            if iscoroutinefunction(cls.bot_entity_descriptor.rls_filters_params):
                params = await cls.bot_entity_descriptor.rls_filters_params(user)
            else:
                params = cls.bot_entity_descriptor.rls_filters_params(user)

        # Create a copy of the RLS filters with parameter values substituted
        rls_filters = _substitute_rls_parameters(
            cls.bot_entity_descriptor.rls_filters, params
        )

        # Apply RLS filters with parameters
        condition = _build_filter_condition(cls, rls_filters)
        if condition is not None:
            return select_statement.where(condition)
    return select_statement


def _substitute_rls_parameters(
    rls_filters: Filter | FilterExpression, params: list[Any]
) -> Filter | FilterExpression:
    """
    Substitute parameter placeholders in RLS filters with actual values.

    Args:
        rls_filters: RLS filters that may contain parameter placeholders
        params: List of parameter values to substitute

    Returns:
        RLS filters with parameters substituted
    """
    # --- Substitute parameter in single filter ---
    if isinstance(rls_filters, Filter):
        if rls_filters.value_type == "param" and rls_filters.param_index is not None:
            if 0 <= rls_filters.param_index < len(params):
                # Create a new filter with the parameter value substituted
                return Filter(
                    field=rls_filters.field,
                    operator=rls_filters.operator,
                    value_type="const",
                    value=params[rls_filters.param_index],
                    param_index=None,
                )
        return rls_filters
    # --- Recursively substitute parameters in all sub-filters ---
    elif isinstance(rls_filters, FilterExpression):
        substituted_filters = []
        for sub_filter in rls_filters.filters:
            substituted_filter = _substitute_rls_parameters(sub_filter, params)
            substituted_filters.append(substituted_filter)
        return FilterExpression(rls_filters.operator, substituted_filters)


def is_bot_entity(type_: type) -> bool:
    return hasattr(type_, "bot_entity_descriptor")


def is_bot_enum(type_: type) -> bool:
    return hasattr(type_, "all_members")
