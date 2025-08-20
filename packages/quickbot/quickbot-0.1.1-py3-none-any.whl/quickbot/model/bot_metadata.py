from fastapi.datastructures import State
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quickbot.main import QuickBot

from .descriptors import EntityDescriptor, ProcessDescriptor
from ._singleton import Singleton


class BotMetadata(metaclass=Singleton):
    def __init__(self):
        self.entity_descriptors: dict[str, EntityDescriptor] = {}
        self.process_descriptors: dict[str, ProcessDescriptor] = {}
        self.app: "QuickBot" = None
        self.app_state: State = None
