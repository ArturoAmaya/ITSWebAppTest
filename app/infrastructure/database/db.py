from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from app.config.environment import get_settings
from app.infrastructure.database.seeds import run as seed_db

_SETTINGS = get_settings()

# TODO implement your own database connection(s)

def init_db():
    SQLModel.metadata.bind = create_engine(_SETTINGS.DATABASE1_URL, connect_args={"check_same_thread": False}, echo=True)

def get_db() -> Generator:
    with Session() as db:
        return db
        
def create_db_and_tables():
    SQLModel.metadata.create_all()
    seed_db(get_db())