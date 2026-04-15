import uuid
from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    icon: str | None = None


class GroupUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    sort_order: int | None = None


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    icon: str | None = None
    sort_order: int
    subscription_count: int = 0
    model_config = {"from_attributes": True}
