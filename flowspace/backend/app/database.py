from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DB_FILE = Path(__file__).resolve().parents[1] / "flowspace.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# echo=True for dev SQL logging
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
