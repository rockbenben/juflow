import uuid
from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str
    color: str | None = None


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagResponse(BaseModel):
    id: uuid.UUID
    name: str
    color: str | None = None
    subscription_count: int = 0
    model_config = {"from_attributes": True}
