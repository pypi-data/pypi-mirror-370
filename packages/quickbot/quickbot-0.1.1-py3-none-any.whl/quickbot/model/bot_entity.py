"""
BotEntity module provides a metaclass and base class for creating database entities
with enhanced functionality for bot operations, including field descriptors,
filtering, and ownership management.
"""

from types import NoneType, UnionType
from typing import (
    Any,
    ClassVar,
    ForwardRef,
    Optional,
    Union,
    get_args,
    get_origin,
    TYPE_CHECKING,
    dataclass_transform,
    Self,
)
from pydantic import BaseModel
from pydantic.fields import _Unset
from pydantic_core import PydanticUndefined
from sqlmodel import SQLModel, BigInteger, Field, select, func
from sqlmodel.main import FieldInfo
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.main import SQLModelMetaclass, RelationshipInfo


from .descriptors import (
    EntityDescriptor,
    EntityField,
    FieldDescriptor,
    Filter,
    FilterExpression,
)
from .bot_metadata import BotMetadata
from .crud_service import CrudService
from . import session_dep
from .utils import (
    _static_filter_condition,
    _build_filter_condition,
    _filter_condition,
    _apply_rls_filters,
)

if TYPE_CHECKING:
    from .user import UserBase


@dataclass_transform(
    kw_only_default=True,
    field_specifiers=(Field, FieldInfo, EntityField, FieldDescriptor),
)
class BotEntityMetaclass(SQLModelMetaclass):
    """
    Metaclass for BotEntity that handles field processing, descriptor creation,
    and type resolution for bot-specific database entities.

    This metaclass extends SQLModelMetaclass to provide additional functionality
    for bot operations including field descriptors, type annotations, and
    entity metadata management.
    """

    # Store future references for forward-declared types
    _future_references = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        """
        Create a new class with processed field descriptors and metadata.

        Args:
            name: Name of the class being created
            bases: Base classes
            namespace: Class namespace containing attributes and annotations
            **kwargs: Additional keyword arguments passed to the metaclass

        Returns:
            The created class with processed field descriptors and metadata
        """
        bot_fields_descriptors = {}

        # --- Inherit field descriptors from parent classes (if any) ---
        if bases:
            bot_entity_descriptor = bases[0].__dict__.get("bot_entity_descriptor")
            bot_fields_descriptors = (
                {
                    key: FieldDescriptor(**value.__dict__.copy())
                    for key, value in bot_entity_descriptor.fields_descriptors.items()
                }
                if bot_entity_descriptor
                else {}
            )

        # --- Process field annotations to create field descriptors ---
        if "__annotations__" in namespace:
            for annotation in namespace["__annotations__"]:
                # Skip special attributes
                if annotation in ["bot_entity_descriptor", "bot_metadata"]:
                    continue

                attribute_value = namespace.get(annotation, PydanticUndefined)

                # Skip relationship fields (handled by SQLModel)
                if isinstance(attribute_value, RelationshipInfo):
                    continue

                descriptor_kwargs = {}
                descriptor_name = annotation

                # --- Process EntityField attributes to extract SQLModel field descriptors ---
                if attribute_value is not PydanticUndefined:
                    if isinstance(attribute_value, EntityField):
                        descriptor_kwargs = attribute_value.__dict__.copy()
                        # Extract SQLModel field descriptor if present
                        sm_descriptor = descriptor_kwargs.pop("sm_descriptor", None)  # type: FieldInfo

                        if sm_descriptor:
                            # Transfer default values from EntityField to SQLModel descriptor
                            if (
                                attribute_value.default is not PydanticUndefined
                                and sm_descriptor.default is PydanticUndefined
                            ):
                                sm_descriptor.default = attribute_value.default
                            if (
                                attribute_value.default_factory is not None
                                and sm_descriptor.default_factory is None
                            ):
                                sm_descriptor.default_factory = (
                                    attribute_value.default_factory
                                )
                            if attribute_value.description is not PydanticUndefined:
                                sm_descriptor.description = attribute_value.description
                        else:
                            # Create new SQLModel field descriptor if none exists
                            if (
                                attribute_value.default is not None
                                or attribute_value.default_factory is not None
                            ):
                                sm_descriptor = Field()
                                if attribute_value.default is not PydanticUndefined:
                                    sm_descriptor.default = attribute_value.default
                                if attribute_value.default_factory is not None:
                                    sm_descriptor.default_factory = (
                                        attribute_value.default_factory
                                    )
                                if attribute_value.description is not PydanticUndefined:
                                    sm_descriptor.description = (
                                        attribute_value.description
                                    )

                        # Clean up internal attributes
                        descriptor_kwargs.pop("__orig_class__", None)

                        # Replace EntityField with SQLModel field descriptor in namespace
                        if sm_descriptor:
                            namespace[annotation] = sm_descriptor
                        else:
                            namespace.pop(annotation)

                        descriptor_name = descriptor_kwargs.pop("name") or annotation

                    elif isinstance(attribute_value, FieldInfo):
                        if attribute_value.default is not PydanticUndefined:
                            descriptor_kwargs["default"] = attribute_value.default
                        if attribute_value.default_factory is not None:
                            descriptor_kwargs["default_factory"] = (
                                attribute_value.default_factory
                            )
                        if attribute_value.description is not _Unset:
                            descriptor_kwargs["description"] = (
                                attribute_value.description
                            )

                    elif isinstance(attribute_value, RelationshipInfo):
                        pass

                    else:
                        descriptor_kwargs["default"] = attribute_value

                # --- Get the type annotation for the field ---
                type_ = namespace["__annotations__"][annotation]

                # --- Create field descriptor with basic information ---
                field_descriptor = FieldDescriptor(
                    name=descriptor_name,
                    field_name=annotation,
                    type_=type_,
                    type_base=type_,
                    **descriptor_kwargs,
                )

                # --- Process type annotations to determine if field is list or optional ---
                type_origin = get_origin(type_)

                is_list = False
                is_optional = False

                # Handle list types (e.g., List[str])
                if type_origin is list:
                    field_descriptor.is_list = is_list = True
                    field_descriptor.type_base = type_ = get_args(type_)[0]

                # Handle Union types for optional fields (e.g., Optional[str])
                if type_origin is Union:
                    args = get_args(type_)
                    if isinstance(args[0], ForwardRef):
                        field_descriptor.is_optional = is_optional = True
                        field_descriptor.type_base = type_ = args[0].__forward_arg__
                    elif args[1] is NoneType:
                        field_descriptor.is_optional = is_optional = True
                        field_descriptor.type_base = type_ = args[0]

                # Handle Python 3.10+ UnionType (e.g., str | None)
                if type_origin is UnionType and get_args(type_)[1] is NoneType:
                    field_descriptor.is_optional = is_optional = True
                    field_descriptor.type_base = type_ = get_args(type_)[0]

                # --- Handle string type references (forward references to other entities) ---
                if isinstance(type_, str):
                    type_not_found = True
                    for entity_descriptor in BotMetadata().entity_descriptors.values():
                        if type_ == entity_descriptor.class_name:
                            # Resolve the type to the actual entity class
                            field_descriptor.type_base = entity_descriptor.type_
                            field_descriptor.type_ = (
                                list[entity_descriptor.type_]
                                if is_list
                                else (
                                    Optional[entity_descriptor.type_]
                                    if type_origin == Union and is_optional
                                    else (
                                        entity_descriptor.type_ | None
                                        if (type_origin == UnionType and is_optional)
                                        else entity_descriptor.type_
                                    )
                                )
                            )
                            type_not_found = False
                            break

                    # If type not found, store for future resolution
                    if type_not_found:
                        if type_ in mcs._future_references:
                            mcs._future_references[type_].append(field_descriptor)
                        else:
                            mcs._future_references[type_] = [field_descriptor]

                bot_fields_descriptors[descriptor_name] = field_descriptor

        # --- Process entity descriptor configuration ---
        descriptor_name = name

        if "bot_entity_descriptor" in namespace:
            # Extract and process custom entity descriptor
            entity_descriptor = namespace.pop("bot_entity_descriptor")
            descriptor_kwargs: dict = entity_descriptor.__dict__.copy()
            descriptor_name = descriptor_kwargs.pop("name", None)
            descriptor_kwargs.pop("__orig_class__", None)
            descriptor_name = descriptor_name or name.lower()
            entity_descriptor = namespace["bot_entity_descriptor"] = EntityDescriptor(
                name=descriptor_name,
                class_name=name,
                type_=name,
                fields_descriptors=bot_fields_descriptors,
                **descriptor_kwargs,
            )
        else:
            # Create default entity descriptor
            descriptor_name = name.lower()
            entity_descriptor = namespace["bot_entity_descriptor"] = EntityDescriptor(
                name=descriptor_name,
                class_name=name,
                type_=name,
                fields_descriptors=bot_fields_descriptors,
            )

        # --- Link field descriptors to their entity descriptor ---
        for field_descriptor in bot_fields_descriptors.values():
            field_descriptor.entity_descriptor = entity_descriptor

        # --- Configure table settings (set to True by default) ---
        if "table" not in kwargs:
            kwargs["table"] = True

        # --- If table is set to True, register entity in global metadata ---
        if kwargs["table"]:
            # Register entity in global metadata
            entity_metadata = BotMetadata()
            entity_metadata.entity_descriptors[descriptor_name] = entity_descriptor

            # Add entity_metadata to class annotations
            if "__annotations__" in namespace:
                namespace["__annotations__"]["bot_metadata"] = ClassVar[BotMetadata]
            else:
                namespace["__annotations__"] = {"bot_metadata": ClassVar[BotMetadata]}

            namespace["bot_metadata"] = entity_metadata

        # --- Create the class using parent metaclass ---
        type_ = super().__new__(mcs, name, bases, namespace, **kwargs)

        # --- Resolve future references now that the class exists ---
        if name in mcs._future_references:
            for field_descriptor in mcs._future_references[name]:
                type_origin = get_origin(field_descriptor.type_)
                field_descriptor.type_base = type_

                field_descriptor.type_ = (
                    list[type_]
                    if type_origin is list
                    else (
                        Optional[type_]
                        if type_origin == Union
                        and isinstance(get_args(field_descriptor.type_)[0], ForwardRef)
                        else type_ | None
                        if type_origin == UnionType
                        else type_
                    )
                )

        # --- Set the resolved type in the entity descriptor ---
        entity_descriptor.type_ = type_
        # setattr(entity_descriptor, "type_", type_)

        if kwargs["table"] and entity_descriptor.crud is None:
            entity_descriptor.crud = CrudService(entity_descriptor)

        return type_


class BotEntity(SQLModel, metaclass=BotEntityMetaclass, table=False):
    """
    Base class for bot entities that provides CRUD operations, filtering,
    and Row Level Security (RLS) capabilities.

    This class extends SQLModel and uses BotEntityMetaclass to provide
    enhanced functionality for bot operations including:
    - Field descriptors for UI generation
    - Advanced filtering and search capabilities
    - Row Level Security (RLS) access control
    - Standardized CRUD operations
    """

    # Class variables set by the metaclass
    bot_entity_descriptor: ClassVar[EntityDescriptor]
    bot_metadata: ClassVar[BotMetadata]

    # Standard ID field for all entities
    id: int = EntityField(
        sm_descriptor=Field(primary_key=True, sa_type=BigInteger),
        is_visible=False,
        default=None,
    )

    @classmethod
    @session_dep
    async def get(
        cls,
        *,
        session: AsyncSession | None = None,
        id: int,
        user: "UserBase | None" = None,
    ) -> Self:
        """
        Retrieve a single entity by ID.

        Args:
            session: Database session (injected by session_dep)
            id: Entity ID to retrieve

        Returns:
            The entity instance or None if not found
        """
        select_statement = select(cls).where(cls.id == id)
        if user:
            select_statement = await _apply_rls_filters(cls, select_statement, user)
        return await session.scalar(select_statement)

    @classmethod
    @session_dep
    async def get_count(
        cls,
        *,
        session: AsyncSession | None = None,
        user: "UserBase",
        static_filter: Filter | FilterExpression | Any = None,
        filter: str = None,
        filter_fields: list[str] = None,
        ext_filter: Any = None,
    ) -> int:
        """
        Get the count of entities matching the specified criteria.

        Args:
            session: Database session (injected by session_dep)
            static_filter: List of static filter conditions
            filter: Text search filter
            filter_fields: Fields to search in for text filter
            ext_filter: Additional custom filter conditions
            user: User for RLS-based filtering

        Returns:
            Count of matching entities
        """
        # --- Build select statement for counting entities ---
        select_statement = select(func.count()).select_from(cls)

        # --- Apply various filter conditions ---
        if static_filter:
            if isinstance(static_filter, list):
                select_statement = _static_filter_condition(
                    select_statement, static_filter
                )
            else:
                # Handle single Filter or FilterExpression object
                condition = _build_filter_condition(cls, static_filter)
                if condition is not None:
                    select_statement = select_statement.where(condition)
        if filter and filter_fields:
            select_statement = _filter_condition(
                select_statement, filter, filter_fields
            )
        if ext_filter:
            select_statement = select_statement.where(ext_filter)

        select_statement = await _apply_rls_filters(cls, select_statement, user)

        return await session.scalar(select_statement)

    @classmethod
    @session_dep
    async def get_multi(
        cls,
        *,
        session: AsyncSession | None = None,
        user: "UserBase | None" = None,
        order_by=None,
        static_filter: Filter | FilterExpression | Any = None,
        filter: str = None,
        filter_fields: list[str] = None,
        ext_filter: Any = None,
        skip: int = 0,
        limit: int = None,
    ) -> list[Self]:
        """
        Retrieve multiple entities with filtering, pagination, and ordering.

        Args:
            session: Database session (injected by session_dep)
            order_by: Ordering criteria
            static_filter: List of static filter conditions
            filter: Text search filter
            filter_fields: Fields to search in for text filter
            ext_filter: Additional custom filter conditions
            user: User for RLS-based filtering
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of matching entity instances
        """
        # --- Build select statement for entity retrieval ---
        select_statement = select(cls).offset(skip)
        if limit:
            select_statement = select_statement.limit(limit)

        # --- Apply various filter conditions ---
        if static_filter is not None:
            if isinstance(static_filter, list):
                select_statement = _static_filter_condition(
                    cls, select_statement, static_filter
                )
            else:
                # Handle single Filter or FilterExpression object
                condition = _build_filter_condition(cls, static_filter)
                if condition is not None:
                    select_statement = select_statement.where(condition)
        if filter and filter_fields:
            select_statement = _filter_condition(
                cls, select_statement, filter, filter_fields
            )
        if ext_filter is not None:
            select_statement = select_statement.where(ext_filter)
        if user:
            select_statement = await _apply_rls_filters(cls, select_statement, user)
        if order_by:
            select_statement = select_statement.order_by(order_by)

        return (await session.exec(select_statement)).all()

    @classmethod
    @session_dep
    async def create(
        cls,
        *,
        session: AsyncSession | None = None,
        obj_in: BaseModel,
        commit: bool = False,
    ) -> Self:
        """
        Create a new entity instance.

        Args:
            session: Database session (injected by session_dep)
            obj_in: Data for creating the entity (can be Pydantic model or entity instance)
            commit: Whether to commit the transaction immediately

        Returns:
            The created entity instance
        """
        # --- Accept both entity instances and Pydantic models ---
        if isinstance(obj_in, cls):
            obj = obj_in
        else:
            obj = cls(**obj_in.model_dump())
        session.add(obj)
        if commit:
            await session.commit()
        return obj

    @classmethod
    @session_dep
    async def update(
        cls,
        *,
        session: AsyncSession | None = None,
        id: int,
        obj_in: BaseModel,
        commit: bool = False,
    ) -> Self:
        """
        Update an existing entity instance.

        Args:
            session: Database session (injected by session_dep)
            id: ID of the entity to update
            obj_in: Data for updating the entity
            commit: Whether to commit the transaction immediately

        Returns:
            The updated entity instance or None if not found
        """
        obj = await session.get(cls, id)
        if obj:
            obj_data = obj.model_dump()
            update_data = obj_in.model_dump(exclude_unset=True)
            # Only update fields present in the update data
            for field in obj_data:
                if field in update_data:
                    setattr(obj, field, update_data[field])
            session.add(obj)
            if commit:
                await session.commit()
            return obj
        return None

    @classmethod
    @session_dep
    async def remove(
        cls, *, session: AsyncSession | None = None, id: int, commit: bool = False
    ) -> Self:
        """
        Delete an entity instance.

        Args:
            session: Database session (injected by session_dep)
            id: ID of the entity to delete
            commit: Whether to commit the transaction immediately

        Returns:
            The deleted entity instance or None if not found
        """
        obj = await session.get(cls, id)
        if obj:
            await session.delete(obj)
            if commit:
                await session.commit()
            return obj
        return None
