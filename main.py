from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from database.connection import conn
from routes.admin import admin_router
from routes.events import event_router
from routes.participants import participant_router
from routes.users import user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()
    yield

app = FastAPI(
    title="Planner API",
    description="Учебное приложение-планировщик событий на FastAPI ",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(user_router, prefix="/user")
app.include_router(event_router, prefix="/event")
app.include_router(participant_router, prefix="/participant")
app.include_router(admin_router, prefix="/admin")

@app.get("/", tags=["Root"])
async def index() -> dict:
    return {"message": "Event Planner API. Документация: /docs"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)