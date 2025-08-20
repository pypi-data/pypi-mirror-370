from pydantic import BaseModel


class ListSchema(BaseModel):
    id: int
    name: str
