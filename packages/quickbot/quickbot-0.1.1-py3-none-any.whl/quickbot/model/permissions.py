from inspect import iscoroutinefunction
from quickbot.model.descriptors import EntityDescriptor, EntityPermission
from quickbot.model.descriptors import Filter, FilterExpression
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickbot.model.user import UserBase
    from quickbot.model.bot_entity import BotEntity


def get_user_permissions(
    user: "UserBase", entity_descriptor: EntityDescriptor
) -> list[EntityPermission]:
    permissions = list[EntityPermission]()
    for permission, roles in entity_descriptor.permissions.items():
        for role in roles:
            if role in user.roles:
                permissions.append(permission)
                break
    return permissions


async def check_entity_permission(
    entity: "BotEntity", user: "UserBase", permission: EntityPermission
) -> bool:
    perm_mapping = {
        EntityPermission.LIST_RLS: EntityPermission.LIST_ALL,
        EntityPermission.READ_RLS: EntityPermission.READ_ALL,
        EntityPermission.UPDATE_RLS: EntityPermission.UPDATE_ALL,
        EntityPermission.CREATE_RLS: EntityPermission.CREATE_ALL,
        EntityPermission.DELETE_RLS: EntityPermission.DELETE_ALL,
    }

    if permission not in perm_mapping:
        raise ValueError(f"Invalid permission: {permission}")

    entity_descriptor = entity.__class__.bot_entity_descriptor
    permissions = get_user_permissions(user, entity_descriptor)

    # Check if user has the corresponding ALL permission
    if perm_mapping[permission] in permissions:
        return True

    # Check RLS filters if they exist
    if entity_descriptor.rls_filters:
        # Get parameters for RLS
        params = []
        if entity_descriptor.rls_filters_params:
            if iscoroutinefunction(entity_descriptor.rls_filters_params):
                params = await entity_descriptor.rls_filters_params(user)
            else:
                params = entity_descriptor.rls_filters_params(user)

        # Create a copy of the RLS filters with parameter values substituted
        rls_filters = entity.__class__._substitute_rls_parameters(
            entity_descriptor.rls_filters, params
        )

        # Check if the entity matches the RLS filters by evaluating the condition
        # against the entity's attributes
        if _entity_matches_rls_filters(entity, rls_filters):
            return True

    # If no RLS filters are defined, check if user has the RLS permission
    if permission in permissions:
        return True

    return False


def _entity_matches_rls_filters(
    entity: "BotEntity", rls_filters: "Filter | FilterExpression"
) -> bool:
    """
    Check if an entity matches the given RLS filters by evaluating the filters
    against the entity's attributes.

    Args:
        entity: The entity to check
        rls_filters: RLS filters to evaluate

    Returns:
        True if the entity matches the filters, False otherwise
    """

    if isinstance(rls_filters, Filter):
        return _evaluate_single_filter(entity, rls_filters)
    elif isinstance(rls_filters, FilterExpression):
        return _evaluate_filter_expression(entity, rls_filters)
    else:
        return False


def _evaluate_single_filter(entity: "BotEntity", filter_obj: "Filter") -> bool:
    """Evaluate a single filter against an entity"""
    # Get the field value from the entity
    if isinstance(filter_obj.field, str):
        field_value = getattr(entity, filter_obj.field, None)
    else:
        # Handle callable field (should return the field name)
        field_name = filter_obj.field(entity.__class__).key
        field_value = getattr(entity, field_name, None)

    # Apply the operator
    if filter_obj.operator == "==":
        return field_value == filter_obj.value
    elif filter_obj.operator == "!=":
        return field_value != filter_obj.value
    elif filter_obj.operator == ">":
        return field_value > filter_obj.value
    elif filter_obj.operator == "<":
        return field_value < filter_obj.value
    elif filter_obj.operator == ">=":
        return field_value >= filter_obj.value
    elif filter_obj.operator == "<=":
        return field_value <= filter_obj.value
    elif filter_obj.operator == "in":
        return field_value in filter_obj.value
    elif filter_obj.operator == "not in":
        return field_value not in filter_obj.value
    elif filter_obj.operator == "like":
        return str(field_value).find(str(filter_obj.value)) != -1
    elif filter_obj.operator == "ilike":
        return str(field_value).lower().find(str(filter_obj.value).lower()) != -1
    elif filter_obj.operator == "is none":
        return field_value is None
    elif filter_obj.operator == "is not none":
        return field_value is not None
    elif filter_obj.operator == "contains":
        return filter_obj.value in field_value
    else:
        return False


def _evaluate_filter_expression(
    entity: "BotEntity", filter_expr: "FilterExpression"
) -> bool:
    """Evaluate a filter expression against an entity"""
    results = []
    for sub_filter in filter_expr.filters:
        if isinstance(sub_filter, Filter):
            result = _evaluate_single_filter(entity, sub_filter)
        elif isinstance(sub_filter, FilterExpression):
            result = _evaluate_filter_expression(entity, sub_filter)
        else:
            result = False
        results.append(result)

    if not results:
        return False

    # Apply the logical operator
    if filter_expr.operator == "and":
        return all(results)
    elif filter_expr.operator == "or":
        return any(results)
    else:
        return False


def _extract_rls_filter_fields(entity_descriptor: EntityDescriptor) -> set[str]:
    return _extract_filter_fields(
        entity_descriptor.rls_filters, entity_descriptor.type_
    )


def _extract_filter_fields(
    filter: Filter | FilterExpression | None, entity_type: type
) -> set[str]:
    fields = set()

    if filter:
        if isinstance(filter, Filter):
            if filter.operator == "==":
                if isinstance(filter.field, str):
                    fields.add(filter.field)
                else:
                    fields.add(filter.field(entity_type).key)

        elif isinstance(filter, FilterExpression):
            if (
                filter.operator == "and"
                and all(isinstance(sub_filter, Filter) for sub_filter in filter.filters)
                and all(sub_filter.operator == "==" for sub_filter in filter.filters)
            ):
                for sub_filter in filter.filters:
                    if isinstance(sub_filter.field, str):
                        fields.add(sub_filter.field)
                    else:
                        fields.add(sub_filter.field(entity_type).key)

    return fields
