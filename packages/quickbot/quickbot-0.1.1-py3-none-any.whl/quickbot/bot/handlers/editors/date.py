from datetime import datetime, time, timedelta
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging import getLogger
from typing import TYPE_CHECKING

from ....model.descriptors import BotContext, FieldDescriptor
from ....model.settings import Settings
from ....model.user import UserBase
from ..context import ContextData, CallbackCommand
from ....utils.main import get_send_message, get_field_descriptor
from .wrapper import wrap_editor

if TYPE_CHECKING:
    from ....main import QuickBot


logger = getLogger(__name__)
router = Router()


@router.callback_query(ContextData.filter(F.command == CallbackCommand.TIME_PICKER))
async def time_picker_callback(
    query: CallbackQuery, callback_data: ContextData, app: "QuickBot", **kwargs
):
    if not callback_data.data:
        return

    field_descriptor = get_field_descriptor(app, callback_data)
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    await time_picker(
        query.message,
        field_descriptor=field_descriptor,
        callback_data=callback_data,
        current_value=datetime.strptime(callback_data.data, "%Y-%m-%d %H-%M")
        if len(callback_data.data) > 10
        else time.fromisoformat(callback_data.data.replace("-", ":")),
        **kwargs,
    )


async def time_picker(
    message: Message | CallbackQuery,
    field_descriptor: FieldDescriptor,
    callback_data: ContextData,
    current_value: datetime | time,
    state: FSMContext,
    user: UserBase,
    edit_prompt: str | None = None,
    **kwargs,
):
    keyboard_builder = InlineKeyboardBuilder()

    if not current_value:
        current_value = time(0, 0)
        is_datetime = False
    else:
        is_datetime = isinstance(current_value, datetime)
        if not is_datetime:
            current_time = datetime.combine(datetime.now(), current_value)
        remainder = current_value.minute % 5
        if remainder >= 3:
            current_time += timedelta(minutes=(5 - remainder))
        else:
            current_time -= timedelta(minutes=remainder)
        if is_datetime:
            current_value = datetime.combine(current_value.date(), current_time.time())
        else:
            current_value = current_time.time()

    for i in range(12):
        keyboard_builder.row(
            InlineKeyboardButton(
                text=(
                    "▶︎ {v:02d} ◀︎" if i == (current_value.hour % 12) else "{v:02d}"
                ).format(v=i if current_value.hour < 12 else i + 12),
                callback_data=ContextData(
                    command=CallbackCommand.TIME_PICKER,
                    context=callback_data.context,
                    entity_name=callback_data.entity_name,
                    entity_id=callback_data.entity_id,
                    field_name=callback_data.field_name,
                    form_params=callback_data.form_params,
                    user_command=callback_data.user_command,
                    data=current_value.replace(
                        hour=i if current_value.hour < 12 else i + 12
                    ).strftime(
                        "%Y-%m-%d %H-%M"
                        if isinstance(current_value, datetime)
                        else "%H-%M"
                    )
                    if i != current_value.hour % 12
                    else None,
                ).pack(),
            ),
            InlineKeyboardButton(
                text=(
                    "▶︎ {v:02d} ◀︎" if i == current_value.minute // 5 else "{v:02d}"
                ).format(v=i * 5),
                callback_data=ContextData(
                    command=CallbackCommand.TIME_PICKER,
                    context=callback_data.context,
                    entity_name=callback_data.entity_name,
                    entity_id=callback_data.entity_id,
                    field_name=callback_data.field_name,
                    form_params=callback_data.form_params,
                    user_command=callback_data.user_command,
                    data=current_value.replace(minute=i * 5).strftime(
                        "%Y-%m-%d %H-%M"
                        if isinstance(current_value, datetime)
                        else "%H-%M"
                    )
                    if i != current_value.minute // 5
                    else None,
                ).pack(),
            ),
        )
    keyboard_builder.row(
        InlineKeyboardButton(
            text="AM/PM",
            callback_data=ContextData(
                command=CallbackCommand.TIME_PICKER,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=current_value.replace(
                    hour=current_value.hour + 12
                    if current_value.hour < 12
                    else current_value.hour - 12
                ).strftime(
                    "%Y-%m-%d %H-%M" if isinstance(current_value, datetime) else "%H-%M"
                ),
            ).pack(),
        ),
        InlineKeyboardButton(
            text=await Settings.get(Settings.APP_STRINGS_DONE_BTN),
            callback_data=ContextData(
                command=CallbackCommand.FIELD_EDITOR_CALLBACK,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=current_value.strftime(
                    "%Y-%m-%d %H-%M" if isinstance(current_value, datetime) else "%H-%M"
                ),
            ).pack(),
        ),
    )

    state_data = kwargs["state_data"]
    context = BotContext(
        db_session=kwargs["db_session"],
        app=kwargs["app"],
        app_state=kwargs["app_state"],
        user=user,
        message=message,
    )

    await wrap_editor(
        keyboard_builder=keyboard_builder,
        field_descriptor=field_descriptor,
        callback_data=callback_data,
        state_data=state_data,
        user=user,
        context=context,
    )

    await state.set_data(state_data)

    if edit_prompt:
        send_message = get_send_message(message)
        await send_message(text=edit_prompt, reply_markup=keyboard_builder.as_markup())
    else:
        await message.edit_reply_markup(reply_markup=keyboard_builder.as_markup())


async def date_picker(
    message: Message | CallbackQuery,
    field_descriptor: FieldDescriptor,
    callback_data: ContextData,
    current_value: datetime,
    state: FSMContext,
    user: UserBase,
    edit_prompt: str | None = None,
    **kwargs,
):
    if not current_value:
        start_date = datetime.now()
    else:
        start_date = current_value

    start_date = start_date.replace(day=1)

    previous_month = start_date - timedelta(days=1)
    next_month = start_date.replace(day=28) + timedelta(days=4)

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(
            text="◀️",
            callback_data=ContextData(
                command=CallbackCommand.DATE_PICKER_MONTH,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=previous_month.strftime("%Y-%m-%d %H-%M"),
            ).pack(),
        ),
        InlineKeyboardButton(
            text=start_date.strftime("%b %Y"),
            callback_data=ContextData(
                command=CallbackCommand.DATE_PICKER_YEAR,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=start_date.strftime("%Y-%m-%d %H-%M"),
            ).pack(),
        ),
        InlineKeyboardButton(
            text="▶️",
            callback_data=ContextData(
                command=CallbackCommand.DATE_PICKER_MONTH,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=next_month.strftime("%Y-%m-%d %H-%M"),
            ).pack(),
        ),
    )

    first_day = start_date - timedelta(days=start_date.weekday())
    weeks = (
        (
            (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - first_day
        ).days
        - 1
    ) // 7 + 1
    for week in range(weeks):
        buttons = []
        for day in range(7):
            current_day = first_day + timedelta(days=week * 7 + day)
            buttons.append(
                InlineKeyboardButton(
                    text=current_day.strftime("%d"),
                    callback_data=ContextData(
                        command=CallbackCommand.FIELD_EDITOR_CALLBACK
                        if field_descriptor.dt_type == "date"
                        else CallbackCommand.TIME_PICKER,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data=current_day.strftime("%Y-%m-%d %H-%M"),
                    ).pack(),
                )
            )

        keyboard_builder.row(*buttons)

    state_data = kwargs["state_data"]

    context = BotContext(
        db_session=kwargs["db_session"],
        app=kwargs["app"],
        app_state=kwargs["app_state"],
        user=user,
        message=message,
    )

    await wrap_editor(
        keyboard_builder=keyboard_builder,
        field_descriptor=field_descriptor,
        callback_data=callback_data,
        state_data=state_data,
        user=user,
        context=context,
    )

    await state.set_data(state_data)

    if edit_prompt:
        send_message = get_send_message(message)
        await send_message(text=edit_prompt, reply_markup=keyboard_builder.as_markup())
    else:
        await message.edit_reply_markup(reply_markup=keyboard_builder.as_markup())


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.DATE_PICKER_YEAR)
)
async def date_picker_year(
    query: CallbackQuery,
    callback_data: ContextData,
    state: FSMContext,
    user: UserBase,
    **kwargs,
):
    app: "QuickBot" = kwargs["app"]
    start_date = datetime.strptime(callback_data.data, "%Y-%m-%d %H-%M")

    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(
            text="🔼",
            callback_data=ContextData(
                command=CallbackCommand.DATE_PICKER_YEAR,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=start_date.replace(year=start_date.year - 20).strftime(
                    "%Y-%m-%d %H-%M"
                ),
            ).pack(),
        )
    )

    for r in range(4):
        buttons = []
        for c in range(5):
            current_date = start_date.replace(year=start_date.year + r * 5 + c - 10)
            buttons.append(
                InlineKeyboardButton(
                    text=current_date.strftime("%Y"),
                    callback_data=ContextData(
                        command=CallbackCommand.DATE_PICKER_MONTH,
                        context=callback_data.context,
                        entity_name=callback_data.entity_name,
                        entity_id=callback_data.entity_id,
                        field_name=callback_data.field_name,
                        form_params=callback_data.form_params,
                        user_command=callback_data.user_command,
                        data=current_date.strftime("%Y-%m-%d %H-%M"),
                    ).pack(),
                )
            )

        keyboard_builder.row(*buttons)

    keyboard_builder.row(
        InlineKeyboardButton(
            text="🔽",
            callback_data=ContextData(
                command=CallbackCommand.DATE_PICKER_YEAR,
                context=callback_data.context,
                entity_name=callback_data.entity_name,
                entity_id=callback_data.entity_id,
                field_name=callback_data.field_name,
                form_params=callback_data.form_params,
                user_command=callback_data.user_command,
                data=start_date.replace(year=start_date.year + 20).strftime(
                    "%Y-%m-%d %H-%M"
                ),
            ).pack(),
        )
    )

    field_descriptor = get_field_descriptor(app, callback_data)

    context = BotContext(
        db_session=kwargs["db_session"],
        app=app,
        app_state=kwargs["app_state"],
        user=user,
        message=query,
    )

    await wrap_editor(
        keyboard_builder=keyboard_builder,
        field_descriptor=field_descriptor,
        callback_data=callback_data,
        state_data=state_data,
        user=user,
        context=context,
    )

    await query.message.edit_reply_markup(reply_markup=keyboard_builder.as_markup())


@router.callback_query(
    ContextData.filter(F.command == CallbackCommand.DATE_PICKER_MONTH)
)
async def date_picker_month(query: CallbackQuery, callback_data: ContextData, **kwargs):
    app: "QuickBot" = kwargs["app"]
    field_descriptor = get_field_descriptor(app, callback_data)
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()
    kwargs["state_data"] = state_data

    await date_picker(
        query.message,
        field_descriptor=field_descriptor,
        callback_data=callback_data,
        current_value=datetime.strptime(callback_data.data, "%Y-%m-%d %H-%M"),
        **kwargs,
    )
