from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    current_time = datetime.now(timezone.utc)
    for task in tasks:
        if task.due_date and task.due_date.tzinfo is None:
            task.due_date = task.due_date.replace(tzinfo=timezone.utc)

    context = {"request": request, "tasks": tasks, "current_time": current_time}
    return templates.TemplateResponse("index.html", context)


@app.post("/tasks/")
def create_task_from_form(
    title: str = Form(...),
    description: str = Form(None),
    due_date: str = Form(None),
    db: Session = Depends(get_db),
):
    due_date_obj = None
    if due_date:
        naive_datetime = datetime.fromisoformat(due_date)
        due_date_obj = naive_datetime.astimezone(timezone.utc)

    task_schema = schemas.TaskCreate(
        title=title, description=description, due_date=due_date_obj
    )
    crud.create_task(db=db, task=task_schema)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/tasks/{task_id}/complete")
def complete_task_from_form(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task:
        update_data = schemas.TaskUpdate(is_done=True)
        crud.update_task(db, task_id=task_id, task_update=update_data)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/tasks/{task_id}/reactivate")
def reactivate_task_from_form(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task:
        update_data = {"is_done": False}
        if (
            task.due_date
            and task.due_date.tzinfo is not None
            and task.due_date < datetime.now(timezone.utc)
        ):
            update_data["due_date"] = None

        task_update_schema = schemas.TaskUpdate(**update_data)
        crud.update_task(db, task_id=task_id, task_update=task_update_schema)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/tasks/{task_id}/delete")
def delete_task_from_form(task_id: int, db: Session = Depends(get_db)):
    """Удаляет задачу и перенаправляет на главную."""
    crud.delete_task(db, task_id=task_id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/api/tasks/", response_model=list[schemas.Task])
def read_tasks_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.get("/api/tasks/{task_id}", response_model=schemas.Task)
def read_task_api(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.get("/health")
def health_check():
    return {"status": "ok"}
