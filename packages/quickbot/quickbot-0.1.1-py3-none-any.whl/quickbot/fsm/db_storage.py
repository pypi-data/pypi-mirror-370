from aiogram.fsm.state import State
from aiogram.fsm.storage.base import (
    BaseStorage,
    StorageKey,
    StateType,
    DefaultKeyBuilder,
    KeyBuilder,
)
from sqlmodel import select
from typing import Any, Dict
import ujson as json

from ..db import async_session
from ..model.fsm_storage import FSMStorage


class DbStorage(BaseStorage):
    def __init__(self, key_builder: KeyBuilder | None = None) -> None:
        if key_builder is None:
            key_builder = DefaultKeyBuilder()
        self.key_builder = key_builder

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        db_key = self.key_builder.build(key, "state")
        async with async_session() as session:
            db_state = (
                await session.exec(select(FSMStorage).where(FSMStorage.key == db_key))
            ).first()

            if db_state:
                if state is None:
                    await session.delete(db_state)
                else:
                    db_state.value = state.state if isinstance(state, State) else state
            elif state is not None:
                db_state = FSMStorage(
                    key=db_key, value=state.state if isinstance(state, State) else state
                )
                session.add(db_state)
            else:
                return

            await session.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        db_key = self.key_builder.build(key, "state")
        async with async_session() as session:
            db_state = (
                await session.exec(select(FSMStorage).where(FSMStorage.key == db_key))
            ).first()
            return db_state.value if db_state else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        db_key = self.key_builder.build(key, "data")
        async with async_session() as session:
            db_data = (
                await session.exec(select(FSMStorage).where(FSMStorage.key == db_key))
            ).first()

            if db_data:
                if not data:
                    await session.delete(db_data)
                else:
                    db_data.value = json.dumps(data, ensure_ascii=False)
            elif data:
                db_data = FSMStorage(
                    key=db_key, value=json.dumps(data, ensure_ascii=False)
                )
                session.add(db_data)
            else:
                return

            await session.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        db_key = self.key_builder.build(key, "data")
        async with async_session() as session:
            db_data = (
                await session.exec(select(FSMStorage).where(FSMStorage.key == db_key))
            ).first()
        return json.loads(db_data.value) if db_data else {}

    async def close(self):
        return await super().close()
