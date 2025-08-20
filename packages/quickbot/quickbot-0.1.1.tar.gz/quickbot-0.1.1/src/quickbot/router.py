from functools import wraps
from types import UnionType
from typing import Callable, Union, get_args, get_origin

from .model.descriptors import (
    BotCommand,
    CommandCallbackContext,
    FieldDescriptor,
    FormField,
)


class Router:
    def __init__(self):
        self._commands = dict[str, BotCommand]()

    def command(
        self,
        name: str,
        caption: str | dict[str, str] | None = None,
        pre_check: Callable[[CommandCallbackContext], bool] | None = None,
        show_in_bot_commands: bool = False,
        register_navigation: bool = True,
        clear_navigation: bool = False,
        clear_state: bool = True,
        show_cancel_in_param_form: bool = True,
        show_back_in_param_form: bool = True,
        form_fields: list[FormField] = list[FormField](),
    ):
        def decorator(func: Callable[[CommandCallbackContext], None]):
            form_fields_dict = dict[str, FieldDescriptor]()
            for field in form_fields:
                is_list = False
                is_optional = False
                type_origin = get_origin(field.type_)
                if type_origin is list:
                    is_list = True
                    type_base = get_args(field.type_)[0]
                elif type_origin in [Union, UnionType] and type(None) in get_args(
                    field.type_
                ):
                    is_optional = True
                    type_base = get_args(field.type_)[0]
                else:
                    type_base = field.type_

                form_fields_dict[field.name] = FieldDescriptor(
                    field_name=field.name,
                    type_base=type_base,
                    is_list=is_list,
                    is_optional=is_optional,
                    **field.__dict__,
                )

            cmd = BotCommand(
                name=name,
                caption=caption,
                pre_check=pre_check,
                show_in_bot_commands=show_in_bot_commands,
                register_navigation=register_navigation,
                clear_navigation=clear_navigation,
                clear_state=clear_state,
                param_form=form_fields_dict,
                show_cancel_in_param_form=show_cancel_in_param_form,
                show_back_in_param_form=show_back_in_param_form,
                handler=func,
            )
            for field in form_fields_dict.values():
                field.command = cmd

            self._commands[cmd.name] = cmd

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator
