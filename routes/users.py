from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database.connection import get_session
from models.users import User, UserCreate, UserSignIn

user_router = APIRouter(tags=["User"])

@user_router.post("/signup")
async def sign_new_user(data: UserCreate, session: Session = Depends(get_session)) -> dict:
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied email already exists",
        )

    user = User(email=data.email, password=data.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User successfully registered!", "id": user.id}

@user_router.post("/signin")
async def sign_user_in(user: UserSignIn, session: Session = Depends(get_session)) -> dict:
    stored = session.exec(select(User).where(User.email == user.email)).first()
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    if stored.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong credentials passed",
        )

    return {"message": "User signed in successfully", "id": stored.id}