from typing import Optional
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

class Participant(SQLModel, table=True):
    __tablename__ = "participant"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")

    model_config = ConfigDict(
        json_schema_extra={"example": {"user_id": 1, "event_id": 1}}
    )

class ParticipantCreate(SQLModel):
    user_id: int
    event_id: int

    model_config = ConfigDict(
        json_schema_extra={"example": {"user_id": 1, "event_id": 1}}
    )