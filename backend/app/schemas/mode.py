from pydantic import BaseModel, ConfigDict


class ModeRead(BaseModel):
    id: int
    name: str
    is_active_default: bool

    model_config = ConfigDict(from_attributes=True)


class ModeActivate(BaseModel):
    mode_id: int
