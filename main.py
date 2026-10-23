import uvicorn
from fastapi import FastAPI

from routes.events import event_router
from routes.users import user_router

app = FastAPI(
    title="Planner API",
    description="Учебное приложение-планировщик событий на FastAPI "
    "(структурирование маршрутов и моделей).",
    version="1.0.0",
)

app.include_router(user_router, prefix="/user")
app.include_router(event_router, prefix="/event")


@app.get("/", tags=["Root"])
async def index() -> dict:
    """Корневой маршрут - проверка работоспособности API."""
    return {"message": "Event Planner API. Документация: /docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)