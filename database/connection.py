import os
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine

BASE_DIR = Path(__file__).resolve().parents[1]
database_file = os.getenv("DB_FILE", str(BASE_DIR / "planner.db"))

database_connection_string = f"sqlite:///{database_file}"

connect_args = {"check_same_thread": False}

echo = os.getenv("DB_ECHO", "0") == "1"

engine_url = create_engine(
    database_connection_string,
    echo=echo,
    connect_args=connect_args,
)

def conn() -> None:
    SQLModel.metadata.create_all(engine_url)

def get_session():
    with Session(engine_url) as session:
        yield session