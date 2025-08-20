from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from quickbot.model.permissions import get_user_permissions
from quickbot.model.descriptors import EntityDescriptor, BotContext
from quickbot.model.crud_command import CrudCommand
from quickbot.model.utils import (
    entity_to_schema,
    entity_to_list_schema,
    pydantic_model,
)
from quickbot.model.descriptors import EntityPermission
from sqlalchemy.exc import IntegrityError
from asyncpg import ForeignKeyViolationError
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickbot.model.user import UserBase

logger = getLogger(__name__)


class NotFoundError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class CrudService:
    def __init__(
        self,
        entity_descriptor: EntityDescriptor,
        commands: list[CrudCommand] = [
            CrudCommand.LIST,
            CrudCommand.GET_BY_ID,
            CrudCommand.CREATE,
            CrudCommand.UPDATE,
            CrudCommand.DELETE,
        ],
        schema: type[BaseModel] = None,
        create_schema: type[BaseModel] = None,
        update_schema: type[BaseModel] = None,
    ):
        self.entity_descriptor = entity_descriptor
        self.commands = commands
        if CrudCommand.CREATE in commands:
            self.create_schema = create_schema or pydantic_model(
                entity_descriptor, entity_descriptor.type_.__module__, "create"
            )
        else:
            self.create_schema = None
        if CrudCommand.UPDATE in commands:
            self.update_schema = update_schema or pydantic_model(
                entity_descriptor, entity_descriptor.type_.__module__, "update"
            )
        else:
            self.update_schema = None
        self.schema = schema or pydantic_model(
            entity_descriptor, entity_descriptor.type_.__module__
        )

    async def list_all(
        self, db_session: AsyncSession, user: "UserBase"
    ) -> list[BaseModel]:
        if CrudCommand.LIST not in self.commands:
            raise ForbiddenError(
                f"List command not allowed for entity {self.entity_descriptor.name}"
            )
        user_permissions = get_user_permissions(user, self.entity_descriptor)
        if (
            EntityPermission.READ_ALL in user_permissions
            or EntityPermission.READ_RLS in user_permissions
        ):
            ret_list = await self.entity_descriptor.type_.get_multi(
                session=db_session,
                user=user
                if EntityPermission.READ_ALL not in user_permissions
                else None,
            )
            return [entity_to_schema(item) for item in ret_list]
        elif (
            EntityPermission.LIST_ALL in user_permissions
            or EntityPermission.LIST_RLS in user_permissions
        ):
            ret_list = await self.entity_descriptor.type_.get_multi(
                session=db_session,
                user=user
                if EntityPermission.LIST_ALL not in user_permissions
                else None,
            )
            context = BotContext(
                db_session=db_session,
                app=user.bot_metadata.app,
                app_state=user.bot_metadata.app_state,
                user=user,
            )
            return [await entity_to_list_schema(item, context) for item in ret_list]
        else:
            raise ForbiddenError(
                f"User {user.id} does not have permission to read or list entities"
            )

    async def get_by_id(
        self, db_session: AsyncSession, user: "UserBase", id: int
    ) -> BaseModel:
        if CrudCommand.GET_BY_ID not in self.commands:
            raise ForbiddenError(
                f"Get by id command not allowed for entity {self.entity_descriptor.name}"
            )
        ret_obj = await self.entity_descriptor.type_.get(session=db_session, id=id)
        if ret_obj is None:
            raise NotFoundError(f"Entity with id {id} not found")
        return entity_to_schema(ret_obj)

    async def create(
        self, db_session: AsyncSession, user: "UserBase", model: BaseModel
    ) -> BaseModel:
        if CrudCommand.CREATE not in self.commands:
            raise ForbiddenError(
                f"Create command not allowed for entity {self.entity_descriptor.name}"
            )
        user_permissions = get_user_permissions(user, self.entity_descriptor)
        if EntityPermission.CREATE_ALL in user_permissions:
            # TODO: check if entity values are valid
            pass
        elif EntityPermission.CREATE_RLS in user_permissions:
            # TODO: check if RLS fields are valid
            # TODO: check if entity values are valid
            pass
        else:
            raise ForbiddenError(
                f"User {user.id} does not have permission to create entities"
            )

        obj_dict = {}
        ret_obj_dict = {}
        for field_descriptor in self.entity_descriptor.fields_descriptors.values():
            # Only process fields present in the input model
            field_name = field_descriptor.field_name
            if field_name in model.__class__.model_fields:
                # Handle list fields that are relations to other BotEntities
                if (
                    field_descriptor.is_list
                    and isinstance(field_descriptor.type_base, type)
                    and hasattr(field_descriptor.type_base, "bot_entity_descriptor")
                ):
                    items = (
                        await db_session.exec(
                            select(field_descriptor.type_base).where(
                                col(field_descriptor.type_base.id).in_(
                                    getattr(model, field_name)
                                )
                            )
                        )
                    ).all()
                    obj_dict[field_name] = items
                    ret_obj_dict[field_name] = [item.id for item in items]
                elif isinstance(field_descriptor.type_base, type) and hasattr(
                    field_descriptor.type_base, "all_members"
                ):
                    if field_descriptor.is_list:
                        obj_dict[field_name] = [
                            field_descriptor.type_base(item)
                            for item in getattr(model, field_name)
                        ]
                    else:
                        obj_dict[field_name] = field_descriptor.type_base(
                            getattr(model, field_name)
                        )
                    ret_obj_dict[field_name] = getattr(model, field_name)
                else:
                    obj_dict[field_name] = getattr(model, field_name)
                    ret_obj_dict[field_name] = getattr(model, field_name)
        obj = self.entity_descriptor.type_(**obj_dict)
        db_session.add(obj)
        try:
            await db_session.commit()
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, ForeignKeyViolationError):
                raise ValueError(e.orig.__cause__.detail)
            raise ValueError("DB Integrity error")
        except Exception as e:
            logger.error(f"Error creating entity: {e}")
            raise e
        if "id" not in ret_obj_dict:
            ret_obj_dict["id"] = obj.id
        return self.schema(**ret_obj_dict)

    async def update(
        self, db_session: AsyncSession, user: "UserBase", id: int, model: BaseModel
    ) -> BaseModel:
        if CrudCommand.UPDATE not in self.commands:
            raise ForbiddenError(
                f"Update command not allowed for entity {self.entity_descriptor.name}"
            )
        user_permissions = get_user_permissions(user, self.entity_descriptor)
        if EntityPermission.UPDATE_ALL in user_permissions:
            # TODO: check if entity values are valid
            pass
        elif EntityPermission.UPDATE_RLS in user_permissions:
            # TODO: check if RLS fields are valid
            # TODO: check if entity values are valid
            pass
        else:
            raise ForbiddenError(
                f"User {user.id} does not have permission to update entities"
            )

        entity = await self.entity_descriptor.type_.get(session=db_session, id=id)
        if entity is None:
            raise NotFoundError(f"Entity with id {id} not found")
        for field_descriptor in self.entity_descriptor.fields_descriptors.values():
            field_name = field_descriptor.field_name
            if field_name in model.model_fields_set:
                model_field_value = getattr(model, field_name)
                if (
                    field_descriptor.is_list
                    and isinstance(field_descriptor.type_base, type)
                    and hasattr(field_descriptor.type_base, "bot_entity_descriptor")
                ):
                    items = (
                        await db_session.exec(
                            select(field_descriptor.type_base).where(
                                col(field_descriptor.type_base.id).in_(
                                    model_field_value
                                )
                            )
                        )
                    ).all()
                    setattr(entity, field_name, items)
                elif isinstance(field_descriptor.type_base, type) and hasattr(
                    field_descriptor.type_base, "all_members"
                ):
                    if field_descriptor.is_list:
                        setattr(
                            entity,
                            field_name,
                            [
                                field_descriptor.type_base(item)
                                for item in model_field_value
                            ],
                        )
                    else:
                        setattr(
                            entity,
                            field_name,
                            field_descriptor.type_base(model_field_value),
                        )
                else:
                    setattr(entity, field_name, model_field_value)
        try:
            await db_session.commit()
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, ForeignKeyViolationError):
                raise ValueError(e.orig.__cause__.detail)
            raise ValueError("DB Integrity error")
        except Exception as e:
            logger.error(f"Error updating entity: {e}")
            raise e
        return entity_to_schema(entity)

    async def delete(
        self, db_session: AsyncSession, user: "UserBase", id: int
    ) -> BaseModel:
        if CrudCommand.DELETE not in self.commands:
            raise ForbiddenError(
                f"Delete command not allowed for entity {self.entity_descriptor.name}"
            )
        user_permissions = get_user_permissions(user, self.entity_descriptor)
        if EntityPermission.DELETE_ALL in user_permissions:
            pass
        elif EntityPermission.DELETE_RLS in user_permissions:
            # TODO: check if RLS fields are valid
            pass
        else:
            raise ForbiddenError(
                f"User {user.id} does not have permission to delete entities"
            )

        try:
            entity = await self.entity_descriptor.type_.remove(
                session=db_session, id=id, commit=True
            )
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, ForeignKeyViolationError):
                raise ValueError(e.orig.__cause__.detail)
            raise ValueError("DB Integrity error")
        except Exception as e:
            logger.error(f"Error deleting entity: {e}")
            raise e
        if entity is None:
            raise NotFoundError(f"Entity with id {id} not found")
        return entity_to_schema(entity)

    # async def _create_from_schema(
    #     cls: type[BotEntity],
    #     *,
    #     session: AsyncSession | None = None,
    #     obj_in: BaseModel,
    # ):
    #     """
    #     Create a new entity instance from a Pydantic model.

    #     Args:
    #         session: Database session (injected by session_dep)
    #         obj_in: Pydantic model to create the entity from

    #     Returns:
    #         The created entity instance
    #     """
    #     obj_dict = {}
    #     ret_obj_dict = {}
    #     for field_descriptor in cls.bot_entity_descriptor.fields_descriptors.values():
    #         # Only process fields present in the input model
    #         if field_descriptor.field_name in obj_in.__class__.model_fields:
    #             # Handle list fields that are relations to other BotEntities
    #             if (
    #                 field_descriptor.is_list
    #                 and isinstance(field_descriptor.type_base, type)
    #                 and issubclass(field_descriptor.type_base, BotEntity)
    #             ):
    #                 items = (
    #                     await session.exec(
    #                         select(field_descriptor.type_base).where(
    #                             col(field_descriptor.type_base.id).in_(
    #                                 getattr(obj_in, field_descriptor.field_name)
    #                             )
    #                         )
    #                     )
    #                 ).all()
    #                 obj_dict[field_descriptor.field_name] = items
    #                 ret_obj_dict[field_descriptor.field_name] = [
    #                     item.id for item in items
    #                 ]
    #             else:
    #                 obj_dict[field_descriptor.field_name] = getattr(
    #                     obj_in, field_descriptor.field_name
    #                 )
    #                 ret_obj_dict[field_descriptor.field_name] = getattr(
    #                     obj_in, field_descriptor.field_name
    #                 )
    #     obj = cls(**obj_dict)
    #     session.add(obj)
    #     await session.commit()
    #     if "id" not in ret_obj_dict:
    #         ret_obj_dict["id"] = obj.id
    #     return cls.bot_entity_descriptor.schema_class(**ret_obj_dict)


# @classmethod
# def apply_filters(
#     cls,
#     select_statement: SelectOfScalar[Self],
#     filters: Filter | FilterExpression | None = None,
# ) -> SelectOfScalar[Self]:
#     """
#     Apply filters to a select statement.

#     Args:
#         select_statement: SQLAlchemy select statement to modify
#         filters: Filter or FilterExpression to apply

#     Returns:
#         Modified select statement with filter conditions
#     """
#     if filters is None:
#         return select_statement
#     condition = cls._build_filter_condition(filters)
#     if condition is not None:
#         return select_statement.where(condition)
#     return select_statement
