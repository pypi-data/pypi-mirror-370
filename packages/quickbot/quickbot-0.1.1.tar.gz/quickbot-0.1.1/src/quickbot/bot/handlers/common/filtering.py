from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ....model.descriptors import BotContext, EntityDescriptor
from ....utils.main import get_callable_str
from ..context import ContextData, CallbackCommand


async def add_filter_controls(
    keyboard_builder: InlineKeyboardBuilder,
    entity_descriptor: EntityDescriptor,
    context: BotContext,
    filter: str = None,
    filtering_fields: list[str] = None,
    page: int = 1,
):
    caption = ", ".join(
        [
            await get_callable_str(
                callable_str=entity_descriptor.fields_descriptors[field_name].caption,
                context=context,
                descriptor=entity_descriptor.fields_descriptors[field_name],
            )
            if entity_descriptor.fields_descriptors[field_name].caption
            else field_name
            for field_name in filtering_fields
        ]
    )

    keyboard_builder.row(
        InlineKeyboardButton(
            text=f"🔎 {caption}{f': "{filter}"' if filter else ''}",
            callback_data=ContextData(
                command=CallbackCommand.VIEW_FILTER_EDIT,
                entity_name=entity_descriptor.name,
                data=str(page),
            ).pack(),
        )
    )
