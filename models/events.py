from typing import List, Optional
from pydantic import ConfigDict
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

class Event(SQLModel, table=True):
    __tablename__ = "event"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    image: str
    description: str
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    location: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": (
                    "We will be discussing the contents of the FastAPI book in "
                    "this event. Ensure to come with your own copy to win gifts!"
                ),
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet",
            }
        }
    )

class EventCreate(SQLModel):
    title: str
    image: str
    description: str
    tags: List[str] = Field(default_factory=list)
    location: str
    owner_id: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": (
                    "We will be discussing the contents of the FastAPI book in "
                    "this event. Ensure to come with your own copy to win gifts!"
                ),
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet",
            }
        }
    )

class EventUpdate(SQLModel):
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    owner_id: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "FastAPI Book Launch (updated)",
                "location": "Offline, Moscow",
            }
        }
    )

UpdateEvent = EventUpdate