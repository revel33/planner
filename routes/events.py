from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session, delete as sql_delete, select
from database.connection import get_session
from models.events import Event, EventCreate, EventUpdate

event_router = APIRouter(tags=["Events"])

@event_router.get("/", response_model=List[Event])
async def retrieve_all_events(session: Session = Depends(get_session)) -> List[Event]:
    statement = select(Event)
    events = session.exec(statement).all()
    return list(events)

@event_router.get("/{id}", response_model=Event)
async def retrieve_event(id: int, session: Session = Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event:
        return event

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event with supplied ID does not exist",
    )


@event_router.post("/new")
async def create_event(
    new_event: EventCreate = Body(...), session: Session = Depends(get_session)
) -> dict:
    event = Event(**new_event.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)  # перечитать строку, чтобы получить присвоенный БД id
    return {"message": "Event created successfully", "id": event.id}

@event_router.put("/{id}", response_model=Event)
async def update_event(
    id: int, new_data: EventCreate = Body(...), session: Session = Depends(get_session)
) -> Event:
    event = session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )

    event_data = new_data.model_dump(exclude={"id"})
    for key, value in event_data.items():
        setattr(event, key, value)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@event_router.patch("/{id}", response_model=Event)
async def patch_event(
    id: int, new_data: EventUpdate = Body(...), session: Session = Depends(get_session)
) -> Event:
    event = session.get(Event, id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )

    event_data = new_data.model_dump(exclude_unset=True)
    for key, value in event_data.items():
        setattr(event, key, value)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@event_router.delete("/{id}")
async def delete_event(id: int, session: Session = Depends(get_session)) -> dict:
    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
        return {"message": "Event deleted successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event with supplied ID does not exist",
    )

@event_router.delete("/")
async def delete_all_events(session: Session = Depends(get_session)) -> dict:
    session.exec(sql_delete(Event))
    session.commit()
    return {"message": "Events deleted successfully"}