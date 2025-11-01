from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from . import database, models, schemas, auth, ai, ws
from typing import List

app = FastAPI(title="FlowSpace Minimal API")
router = APIRouter()
app.include_router(ws.router, prefix="/ws")

# startup hook
@app.on_event("startup")
def on_startup():
    database.init_db()

# token endpoint
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with next(database.get_session()) as session:
        user = auth.authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
        access_token = auth.create_access_token({"sub": user.email}, expires_delta=timedelta(minutes=60))
        return {"access_token": access_token, "token_type": "bearer"}

# register user
@router.post("/register", response_model=schemas.UserOut)
def register_user(payload: schemas.UserCreate):
    with next(database.get_session()) as session:
        existing = session.exec(select(models.User).where(models.User.email == payload.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = auth.get_password_hash(payload.password)
        user = models.User(email=payload.email, hashed_password=hashed, full_name=payload.full_name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return schemas.UserOut.from_orm(user)

# create board
@router.post("/boards")
def create_board(title: str = Body(..., embed=True)):
    with next(database.get_session()) as session:
        b = models.Board(title=title)
        session.add(b)
        session.commit()
        session.refresh(b)
        return {"id": b.id, "title": b.title}

# list boards
@router.get("/boards")
def list_boards():
    with next(database.get_session()) as session:
        boards = session.exec(select(models.Board)).all()
        return boards

# tasks CRUD
@router.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(payload: schemas.TaskCreate):
    with next(database.get_session()) as session:
        t = models.Task(
            title=payload.title,
            description=payload.description,
            status=payload.status or "todo",
            priority=payload.priority or "medium",
            board_id=payload.board_id
        )
        session.add(t)
        session.commit()
        session.refresh(t)
        # broadcast new task on ws for that board
        try:
            import asyncio
            asyncio.create_task(ws.manager.broadcast(str(t.board_id or "global"), {"type":"task_created","task":t.dict()}))
        except Exception:
            pass
        return t

@router.get("/tasks", response_model=List[schemas.TaskOut])
def list_tasks(board_id: int = None):
    with next(database.get_session()) as session:
        q = select(models.Task)
        if board_id:
            q = q.where(models.Task.board_id == board_id)
        tasks = session.exec(q).all()
        return tasks

@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: dict):
    with next(database.get_session()) as session:
        t = session.get(models.Task, task_id)
        if not t:
            raise HTTPException(status_code=404, detail="Task not found")
        for k, v in payload.items():
            if hasattr(t, k):
                setattr(t, k, v)
        session.add(t)
        session.commit()
        session.refresh(t)
        try:
            import asyncio
            asyncio.create_task(ws.manager.broadcast(str(t.board_id or "global"), {"type":"task_updated","task":t.dict()}))
        except Exception:
            pass
        return t

# AI endpoint: extract task from raw email text
processor = ai.AITaskProcessor()

@router.post("/ai/extract")
def ai_extract(email_text: str = Body(..., embed=True)):
    data = processor.extract_task_from_email(email_text)
    return data

app.include_router(router, prefix="/api")
