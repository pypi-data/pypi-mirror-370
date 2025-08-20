from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Any, Callable, TYPE_CHECKING, Literal, Union
from babel.support import LazyProxy
from dataclasses import dataclass, field
from fastapi.datastructures import State
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from .role import RoleBase
from . import EntityPermission
from ..bot.handlers.context import ContextData

if TYPE_CHECKING:
    from .bot_entity import BotEntity
    from ..main import QuickBot
    from .user import UserBase
    from .crud_service import CrudService
    from .bot_process import BotProcess

# EntityCaptionCallable = Callable[["EntityDescriptor"], str]
# EntityItemCaptionCallable = Callable[["EntityDescriptor", Any], str]
# EntityFieldCaptionCallable = Callable[["FieldDescriptor", Any, Any], str]


@dataclass
class FieldEditButton[T: "BotEntity"]:
    field: str | Callable[[type[T]], InstrumentedAttribute]
    caption: str | LazyProxy | Callable[[T, "BotContext"], str] | None = None
    visibility: Callable[[T, "BotContext"], bool] | None = None


@dataclass
class CommandButton[T: "BotEntity"]:
    command: ContextData | Callable[[T, "BotContext"], ContextData] | str
    caption: str | LazyProxy | Callable[[T, "BotContext"], str] | None = None
    visibility: Callable[[T, "BotContext"], bool] | None = None


@dataclass
class InlineButton[T: "BotEntity"]:
    inline_button: (
        InlineKeyboardButton | Callable[[T, "BotContext"], InlineKeyboardButton]
    )
    visibility: Callable[[T, "BotContext"], bool] | None = None


@dataclass
class Filter[T: "BotEntity"]:
    field: str | Callable[[type[T]], InstrumentedAttribute]
    operator: Literal[
        "==",
        "!=",
        ">",
        "<",
        ">=",
        "<=",
        "in",
        "not in",
        "like",
        "ilike",
        "is none",
        "is not none",
        "contains",
    ]
    value_type: Literal["const", "param"] = "const"
    value: Any | None = None
    param_index: int | None = None

    def __or__(self, other: "Filter[T] | FilterExpression[T]") -> "FilterExpression[T]":
        """Create OR expression with another filter or expression"""
        if isinstance(other, Filter):
            return FilterExpression("or", [self, other])
        elif isinstance(other, FilterExpression):
            if other.operator == "or":
                # Simplify: filter | (a | b) = (filter | a | b)
                return FilterExpression("or", [self] + other.filters)
            else:
                return FilterExpression("or", [self, other])
        else:
            raise TypeError(f"Cannot combine Filter with {type(other)}")

    def __and__(
        self, other: "Filter[T] | FilterExpression[T]"
    ) -> "FilterExpression[T]":
        """Create AND expression with another filter or expression"""
        if isinstance(other, Filter):
            return FilterExpression("and", [self, other])
        elif isinstance(other, FilterExpression):
            if other.operator == "and":
                # Simplify: filter & (a & b) = (filter & a & b)
                return FilterExpression("and", [self] + other.filters)
            else:
                return FilterExpression("and", [self, other])
        else:
            raise TypeError(f"Cannot combine Filter with {type(other)}")


class FilterExpression[T: "BotEntity"]:
    """
    Represents a logical expression combining multiple filters with AND/OR operations.
    Supports expression simplification for optimal query building.
    """

    def __init__(
        self,
        operator: Literal["or", "and"],
        filters: list["Filter[T] | FilterExpression[T]"],
    ):
        self.operator = operator
        self.filters = self._simplify_filters(filters)

    def _simplify_filters(
        self, filters: list["Filter[T] | FilterExpression[T]"]
    ) -> list["Filter[T] | FilterExpression[T]"]:
        """Simplify filters by flattening nested expressions with the same operator"""
        simplified = []
        for filter_obj in filters:
            if (
                isinstance(filter_obj, FilterExpression)
                and filter_obj.operator == self.operator
            ):
                # Flatten nested expressions with the same operator
                simplified.extend(filter_obj.filters)
            else:
                simplified.append(filter_obj)
        return simplified

    def __or__(self, other: "Filter[T] | FilterExpression[T]") -> "FilterExpression[T]":
        """Combine with another filter or expression using OR"""
        if isinstance(other, (Filter, FilterExpression)):
            if isinstance(other, FilterExpression) and other.operator == "or":
                # Simplify: (a | b) | (c | d) = (a | b | c | d)
                return FilterExpression("or", self.filters + other.filters)
            else:
                return FilterExpression("or", [self, other])
        else:
            raise TypeError(f"Cannot combine FilterExpression with {type(other)}")

    def __and__(
        self, other: "Filter[T] | FilterExpression[T]"
    ) -> "FilterExpression[T]":
        """Combine with another filter or expression using AND"""
        if isinstance(other, (Filter, FilterExpression)):
            if isinstance(other, FilterExpression) and other.operator == "and":
                # Simplify: (a & b) & (c & d) = (a & b & c & d)
                return FilterExpression("and", self.filters + other.filters)
            else:
                return FilterExpression("and", [self, other])
        else:
            raise TypeError(f"Cannot combine FilterExpression with {type(other)}")


@dataclass
class EntityList[T: "BotEntity"]:
    caption: (
        str | LazyProxy | Callable[["EntityDescriptor", "BotContext"], str] | None
    ) = None
    item_repr: Callable[[T, "BotContext"], str] | None = None
    show_add_new_button: bool = True
    item_form: str | None = None
    pagination: bool = True
    static_filters: Filter[T] | FilterExpression[T] | None = None
    filtering: bool = False
    filtering_fields: list[str] = None
    order_by: str | Any | None = None


@dataclass
class EntityForm[T: "BotEntity"]:
    item_repr: Callable[[T, "BotContext"], str] | None = None
    edit_field_sequence: list[str] = None
    form_buttons: list[list[FieldEditButton | CommandButton | InlineButton]] = None
    show_edit_button: bool = True
    show_delete_button: bool = True
    before_open: Callable[[T, "BotContext"], None] | None = None


@dataclass(kw_only=True)
class _BaseFieldDescriptor[T: "BotEntity"]:
    icon: str = None
    caption: (
        str | LazyProxy | Callable[["FieldDescriptor", "BotContext"], str] | None
    ) = None
    description: str | LazyProxy | None = PydanticUndefined
    edit_prompt: (
        str
        | LazyProxy
        | Callable[["FieldDescriptor", Union[T, Any], "BotContext"], str]
        | None
    ) = None
    caption_value: (
        Callable[["FieldDescriptor", Union[T, Any], "BotContext"], str] | None
    ) = None
    is_visible: bool | Callable[["FieldDescriptor", T, "BotContext"], bool] | None = (
        None
    )
    is_visible_in_edit_form: (
        bool | Callable[["FieldDescriptor", Union[T, Any], "BotContext"], bool] | None
    ) = None
    validator: Callable[[Any, "BotContext"], Union[bool, str]] | None = None
    localizable: bool = False
    bool_false_value: str | LazyProxy = "no"
    bool_true_value: str | LazyProxy = "yes"
    ep_form: str | Callable[["BotContext"], str] | None = None
    ep_parent_field: str | Callable[[type[T]], InstrumentedAttribute] | None = None
    ep_child_field: str | Callable[[type[T]], InstrumentedAttribute] | None = None
    dt_type: Literal["date", "datetime"] = "date"
    options: (
        list[list[Union[Any, tuple[Any, str]]]]
        | Callable[[T, "BotContext"], list[list[Union[Any, tuple[Any, str]]]]]
        | None
    ) = None
    options_custom_value: bool = True
    show_current_value_button: bool = True
    show_skip_in_editor: Literal[False, "Auto"] = "Auto"
    default: Any = PydanticUndefined
    default_factory: Callable[[], Any] | None = None


@dataclass(kw_only=True)
class EntityField[T: "BotEntity"](_BaseFieldDescriptor[T]):
    name: str | None = None
    sm_descriptor: Any = None


@dataclass(kw_only=True)
class Setting(_BaseFieldDescriptor):
    name: str | None = None


@dataclass(kw_only=True)
class FormField[T: "BotEntity"](_BaseFieldDescriptor[T]):
    name: str | None = None
    type_: type


@dataclass(kw_only=True)
class FieldDescriptor(_BaseFieldDescriptor):
    name: str
    field_name: str
    type_: type
    type_base: type = None
    is_list: bool = False
    is_optional: bool = False
    entity_descriptor: "EntityDescriptor" = None
    command: "BotCommand" = None

    def __hash__(self):
        return self.name.__hash__()


@dataclass(kw_only=True)
class _BaseEntityDescriptor[T: "BotEntity"]:
    icon: str = "📘"
    full_name: (
        str | LazyProxy | Callable[["EntityDescriptor", "BotContext"], str] | None
    ) = None
    full_name_plural: (
        str | LazyProxy | Callable[["EntityDescriptor", "BotContext"], str] | None
    ) = None
    description: str | None = None
    ui_description: (
        str | LazyProxy | Callable[["EntityDescriptor", "BotContext"], str] | None
    ) = None
    item_repr: Callable[[T, "BotContext"], str] | None = None
    default_list: EntityList = field(default_factory=EntityList)
    default_form: EntityForm = field(default_factory=EntityForm)
    lists: dict[str, EntityList] = field(default_factory=dict[str, EntityList])
    forms: dict[str, EntityForm] = field(default_factory=dict[str, EntityForm])
    show_in_entities_menu: bool = True
    ownership_fields: dict[RoleBase, str] = field(default_factory=dict[RoleBase, str])
    permissions: dict[EntityPermission, list[RoleBase]] = field(
        default_factory=lambda: {
            EntityPermission.LIST_RLS: [RoleBase.DEFAULT_USER, RoleBase.SUPER_USER],
            EntityPermission.READ_RLS: [RoleBase.DEFAULT_USER, RoleBase.SUPER_USER],
            EntityPermission.CREATE_RLS: [RoleBase.DEFAULT_USER, RoleBase.SUPER_USER],
            EntityPermission.UPDATE_RLS: [RoleBase.DEFAULT_USER, RoleBase.SUPER_USER],
            EntityPermission.DELETE_RLS: [RoleBase.DEFAULT_USER, RoleBase.SUPER_USER],
            EntityPermission.LIST_ALL: [RoleBase.SUPER_USER],
            EntityPermission.READ_ALL: [RoleBase.SUPER_USER],
            EntityPermission.CREATE_ALL: [RoleBase.SUPER_USER],
            EntityPermission.UPDATE_ALL: [RoleBase.SUPER_USER],
            EntityPermission.DELETE_ALL: [RoleBase.SUPER_USER],
        }
    )
    rls_filters: Filter[T] | FilterExpression[T] | None = None
    rls_filters_params: Callable[["UserBase"], list[Any]] = lambda user: [user.id]
    before_create: Callable[["BotContext"], Union[bool, str]] | None = None
    before_create_save: Callable[[T, "BotContext"], Union[bool, str]] | None = None
    before_update_save: (
        Callable[[dict[str, Any], dict[str, Any], "BotContext"], Union[bool, str]]
        | None
    ) = None
    before_delete: Callable[[T, "BotContext"], Union[bool, str]] | None = None
    on_created: Callable[[T, "BotContext"], None] | None = None
    on_deleted: Callable[[T, "BotContext"], None] | None = None
    on_updated: Callable[[dict[str, Any], T, "BotContext"], None] | None = None
    crud: Union["CrudService", None] = None


@dataclass(kw_only=True)
class Entity[T: "BotEntity"](_BaseEntityDescriptor[T]):
    name: str | None = None


@dataclass
class EntityDescriptor(_BaseEntityDescriptor):
    name: str
    class_name: str
    type_: type["BotEntity"]
    fields_descriptors: dict[str, FieldDescriptor]


@dataclass(kw_only=True)
class CommandCallbackContext:
    keyboard_builder: InlineKeyboardBuilder = field(
        default_factory=InlineKeyboardBuilder
    )
    message_text: str | None = None
    register_navigation: bool = True
    clear_navigation: bool = False
    message: Message | CallbackQuery
    callback_data: ContextData
    db_session: AsyncSession
    user: "UserBase"
    app: "QuickBot"
    app_state: State
    state_data: dict[str, Any]
    state: FSMContext
    form_data: dict[str, Any]
    i18n: I18n
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class BotContext:
    db_session: AsyncSession
    app: "QuickBot"
    app_state: State
    user: "UserBase"
    message: Message | CallbackQuery | None = None
    default_handler: Callable[["BotEntity", "BotContext"], None] | None = None


@dataclass(kw_only=True)
class BotCommand:
    name: str
    caption: str | dict[str, str] | None = None
    pre_check: Callable[[Union[Message, CallbackQuery], Any], bool] | None = None
    show_in_bot_commands: bool = False
    register_navigation: bool = True
    clear_navigation: bool = False
    clear_state: bool = True
    param_form: dict[str, FieldDescriptor] | None = None
    show_cancel_in_param_form: bool = True
    show_back_in_param_form: bool = True
    handler: Callable[[CommandCallbackContext], None]


@dataclass(kw_only=True)
class _BaseProcessDescriptor:
    description: str | LazyProxy | None = None
    roles: list[RoleBase] = field(
        default_factory=lambda: [RoleBase.DEFAULT_USER, RoleBase.SUPER_USER]
    )
    icon: str | None = None
    caption: str | LazyProxy | None = None
    pre_check: Callable[[BotContext], bool | str] | None = None
    show_in_bot_menu: bool = False
    answer_message: Callable[[BotContext, BaseModel], str] | None = None
    answer_inline_buttons: (
        Callable[[BotContext, BaseModel], list[InlineKeyboardButton]] | None
    ) = None


@dataclass(kw_only=True)
class ProcessDescriptor(_BaseProcessDescriptor):
    name: str
    process_class: type["BotProcess"]
    input_schema: type[BaseModel] | None = None
    output_schema: type[BaseModel] | None = None


@dataclass(kw_only=True)
class Process(_BaseProcessDescriptor): ...
