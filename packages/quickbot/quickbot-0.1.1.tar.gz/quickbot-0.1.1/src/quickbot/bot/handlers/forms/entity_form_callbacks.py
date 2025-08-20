from inspect import iscoroutinefunction
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import TYPE_CHECKING

from quickbot.model.descriptors import BotContext

from ..context import ContextData, CallbackCommand
from ....model.user import UserBase
from ....model.settings import Settings
from ....model import EntityPermission
from ....model.permissions import check_entity_permission
from ....utils.main import (
    get_entity_item_repr,
    get_entity_descriptor,
)
from ..common.routing import route_callback

if TYPE_CHECKING:
    from ....main import QuickBot


router = Router()


@router.callback_query(ContextData.filter(F.command == CallbackCommand.ENTITY_DELETE))
async def entity_delete_callback(query: CallbackQuery, **kwargs):
    callback_data: ContextData = kwargs["callback_data"]
    user: UserBase = kwargs["user"]
    db_session: AsyncSession = kwargs["db_session"]
    app: "QuickBot" = kwargs["app"]
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    entity_descriptor = get_entity_descriptor(app=app, callback_data=callback_data)

    entity = await entity_descriptor.type_.get(
        session=db_session, id=int(callback_data.entity_id)
    )

    if not await check_entity_permission(
        entity=entity, user=user, permission=EntityPermission.DELETE_RLS
    ):
        return await query.answer(
            text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN))
        )

    context = BotContext(
        db_session=db_session,
        app=app,
        app_state=kwargs["app_state"],
        user=user,
        message=query,
    )

    if callback_data.data == "yes":
        can_delete = True

        if entity_descriptor.before_delete:
            if iscoroutinefunction(entity_descriptor.before_delete):
                can_delete = await entity_descriptor.before_delete(
                    entity,
                    context,
                )
            else:
                can_delete = entity_descriptor.before_delete(
                    entity,
                    context,
                )
            if isinstance(can_delete, str):
                await query.answer(text=can_delete, show_alert=True)
            elif not can_delete:
                await query.answer(
                    text=(await Settings.get(Settings.APP_STRINGS_FORBIDDEN)),
                    show_alert=True,
                )

        if isinstance(can_delete, bool) and can_delete:
            await db_session.delete(entity)
            await db_session.commit()

            if entity_descriptor.on_updated:
                if iscoroutinefunction(entity_descriptor.on_updated):
                    await entity_descriptor.on_updated(
                        entity,
                        context,
                    )
                else:
                    entity_descriptor.on_updated(
                        entity,
                        context,
                    )

            await route_callback(message=query, **kwargs)

        else:
            await route_callback(message=query, back=False, **kwargs)

    elif not callback_data.data:
        entity = await entity_descriptor.type_.get(
            session=db_session, id=int(callback_data.entity_id)
        )

        return await query.message.edit_text(
            text=(
                await Settings.get(Settings.APP_STRINGS_CONFIRM_DELETE_P_NAME)
            ).format(
                name=await get_entity_item_repr(
                    entity=entity,
                    context=context,
                )
            ),
            reply_markup=InlineKeyboardBuilder()
            .row(
                InlineKeyboardButton(
                    text=(await Settings.get(Settings.APP_STRINGS_YES_BTN)),
                    callback_data=ContextData(
                        command=CallbackCommand.ENTITY_DELETE,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        form_params=callback_data.form_params,
                        data="yes",
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=(await Settings.get(Settings.APP_STRINGS_NO_BTN)),
                    callback_data=ContextData(
                        command=CallbackCommand.ENTITY_ITEM,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        form_params=callback_data.form_params,
                    ).pack(),
                ),
            )
            .as_markup(),
        )
