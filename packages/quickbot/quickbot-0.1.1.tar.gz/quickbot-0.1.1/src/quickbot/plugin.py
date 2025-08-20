from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from quickbot import QuickBot


@runtime_checkable
class Registerable(Protocol):
    def register(self, app: "QuickBot") -> None: ...
