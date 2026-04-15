import uuid
from pydantic import BaseModel


class SourceResponse(BaseModel):
    id: uuid.UUID
    platform: str
    platform_uid: str
    display_name: str
    avatar_url: str | None = None
    home_url: str
    adapter_type: str

    model_config = {"from_attributes": True}
