from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..context import ContextData, CallbackCommand


def add_pagination_controls(
    keyboard_builder: InlineKeyboardBuilder,
    callback_data: ContextData,
    total_pages: int,
    command: CallbackCommand,
    page: int,
):
    if total_pages > 1:
        navigation_buttons = []
        # ContextData(**callback_data.model_dump()).__setattr__
        if total_pages > 10:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="⏮️",
                    callback_data=ContextData(
                        command=command,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data="1" if page != 1 else "skip",
                    ).pack(),
                )
            )
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="⏪️",
                    callback_data=ContextData(
                        command=command,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data=str(max(page - 10, 1)) if page > 1 else "skip",
                    ).pack(),
                )
            )

        navigation_buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=ContextData(
                    command=command,
                    context=callback_data.context,
                    entity_name=callback_data.entity_name,
                    entity_id=callback_data.entity_id,
                    field_name=callback_data.field_name,
                    form_params=callback_data.form_params,
                    user_command=callback_data.user_command,
                    data=str(max(page - 1, 1)) if page > 1 else "skip",
                ).pack(),
            )
        )
        navigation_buttons.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=ContextData(
                    command=command,
                    context=callback_data.context,
                    entity_name=callback_data.entity_name,
                    entity_id=callback_data.entity_id,
                    field_name=callback_data.field_name,
                    form_params=callback_data.form_params,
                    user_command=callback_data.user_command,
                    data=(
                        str(min(page + 1, total_pages))
                        if page < total_pages
                        else "skip"
                    ),
                ).pack(),
            )
        )

        if total_pages > 10:
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="⏩️",
                    callback_data=ContextData(
                        command=command,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data=(
                            str(min(page + 10, total_pages))
                            if page < total_pages
                            else "skip"
                        ),
                    ).pack(),
                )
            )
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="⏭️",
                    callback_data=ContextData(
                        command=command,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data=str(total_pages) if page != total_pages else "skip",
                    ).pack(),
                )
            )

        keyboard_builder.row(*navigation_buttons)
