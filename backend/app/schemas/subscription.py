import uuid
from pydantic import BaseModel, Field

from app.schemas.source import SourceResponse


class SubscriptionCreate(BaseModel):
    url: str
    fetch_interval: int = Field(default=300, ge=60)
    notify_enabled: bool = True


class SubscriptionUpdate(BaseModel):
    custom_name: str | None = None
    fetch_interval: int | None = Field(default=None, ge=60)
    notify_enabled: bool | None = None
    notify_channels: list[str] | None = None
    dnd_exempt: bool | None = None
    group_ids: list[uuid.UUID] | None = None
    tag_ids: list[uuid.UUID] | None = None


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    source: SourceResponse
    fetch_interval: int
    notify_enabled: bool
    notify_channels: list[str]
    custom_name: str | None = None

    model_config = {"from_attributes": True}
