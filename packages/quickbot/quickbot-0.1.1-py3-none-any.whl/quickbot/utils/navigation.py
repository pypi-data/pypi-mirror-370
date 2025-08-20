from ..bot.handlers.context import ContextData, CallbackCommand


def save_navigation_context(
    callback_data: ContextData, state_data: dict
) -> list[ContextData]:
    stack = [
        ContextData.unpack(item) for item in state_data.get("navigation_stack", [])
    ]
    data_nc = state_data.get("navigation_context")
    navigation_context = ContextData.unpack(data_nc) if data_nc else None
    if callback_data.back:
        callback_data.back = False
        if stack:
            stack.pop()
    else:
        if (
            stack
            and navigation_context
            and navigation_context.command == callback_data.command
            and navigation_context.entity_name == callback_data.entity_name
            and navigation_context.entity_id == callback_data.entity_id
            and navigation_context.command != CallbackCommand.USER_COMMAND
        ):
            navigation_context = callback_data
        elif navigation_context:
            stack.append(navigation_context)

    state_data["navigation_stack"] = [item.pack() for item in stack]
    state_data["navigation_context"] = callback_data.pack()

    return stack


def pop_navigation_context(stack: list[ContextData]) -> ContextData | None:
    if stack:
        data = stack[-1]
        data.back = True
        return data


def get_navigation_context(
    state_data: dict,
) -> tuple[list[ContextData], ContextData | None]:
    data_nc = state_data.get("navigation_context")
    context = ContextData.unpack(data_nc) if data_nc else None
    return (
        [ContextData.unpack(item) for item in state_data.get("navigation_stack", [])],
        context,
    )
