from sqlmodel import SQLModel, Field


class FSMStorage(SQLModel, table=True):
    __tablename__ = "fsm_storage"
    key: str = Field(primary_key=True)
    value: str | None = None
