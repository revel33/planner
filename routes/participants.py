from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database.connection import get_session
from models.events import Event
from models.participants import Participant, ParticipantCreate
from models.users import User

participant_router = APIRouter(tags=["Participant"])

@participant_router.get("/", response_model=List[Participant])
async def list_participants(session: Session = Depends(get_session)) -> List[Participant]:
    return session.exec(select(Participant)).all()

@participant_router.post("/new")
async def add_participant(
    data: ParticipantCreate, session: Session = Depends(get_session)
) -> dict:
    if not session.get(User, data.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {data.user_id} does not exist",
        )
    if not session.get(Event, data.event_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {data.event_id} does not exist",
        )

    participant = Participant(user_id=data.user_id, event_id=data.event_id)
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return {"message": "Participant added successfully", "id": participant.id}

@participant_router.delete("/{id}")
async def remove_participant(id: int, session: Session = Depends(get_session)) -> dict:
    """Убрать запись на событие."""
    participant = session.get(Participant, id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant with supplied ID does not exist",
        )

    session.delete(participant)
    session.commit()
    return {"message": "Participant removed successfully"}