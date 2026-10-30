from typing import Optional
from pydantic import ConfigDict, EmailStr
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "fastapi@packt.com", "password": "strong!!!"}
        }
    )

class UserCreate(SQLModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "fastapi@packt.com", "password": "strong!!!"}
        }
    )

class UserSignIn(SQLModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "fastapi@packt.com", "password": "strong!!!"}
        }
    )

NewUser = UserCreate