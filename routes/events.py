from typing import List
from fastapi import APIRouter, Body, HTTPException, status
from models.events import Event, UpdateEvent

event_router = APIRouter(tags=["Events"])

events: List[Event] = []

@event_router.get("/", response_model=List[Event])
async def retrieve_all_events() -> List[Event]:
    return events


@event_router.get("/{id}", response_model=Event)
async def retrieve_event(id: int) -> Event:
    for event in events:
        if event.id == id:
            return event

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event with supplied ID does not exist",
    )


@event_router.post("/new")
async def create_event(body: Event = Body(...)) -> dict:
    events.append(body)
    return {"message": "Event created successfully"}


@event_router.put("/{id}", response_model=Event)
async def update_event(id: int, body: Event = Body(...)) -> Event:
    for index, event in enumerate(events):
        if event.id == id:
            updated = body.model_copy(update={"id": id})
            events[index] = updated
            return updated

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event with supplied ID does not exist",
    )


@event_router.patch("/{id}", response_model=Event)
async def patch_event(id: int, body: UpdateEvent = Body(...)) -> Event:
    for index, event in enumerate(events):
        if event.id == id:
            changes = body.model_dump(exclude_unset=True)
            updated = event.model_copy(update=changes)
            events[index] = updated
            return updated

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event with supplied ID does not exist",
    )


@event_router.delete("/{id}")
async def delete_event(id: int) -> dict:
    for event in events:
        if event.id == id:
            events.remove(event)
            return {"message": "Event deleted successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Event with supplied ID does not exist",
    )


@event_router.delete("/")
async def delete_all_events() -> dict:
    events.clear()
    return {"message": "Events deleted successfully"}