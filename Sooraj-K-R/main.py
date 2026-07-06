from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional

app = FastAPI()
todos_db = []
id_counter = 0


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TodoCreate(BaseModel):
    title: str
    checked: bool = False
    priority: Priority

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError("title must be a non-empty string")
        if len(v.strip()) < 3:
            raise ValueError("title must be at least 3 characters long")
        return v.strip()

    @field_validator("priority", mode="before")
    @classmethod
    def priority_must_be_valid(cls, v):
        allowed = {"low", "medium", "high"}
        if isinstance(v, str) and v.lower() not in allowed:
            raise ValueError(f"invalid priority '{v}', must be one of: low, medium, high")
        return v


class TodoUpdate(BaseModel):
    title: str
    checked: bool
    priority: Priority

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError("title must be a non-empty string")
        if len(v.strip()) < 3:
            raise ValueError("title must be at least 3 characters long")
        return v.strip()

    @field_validator("priority", mode="before")
    @classmethod
    def priority_must_be_valid(cls, v):
        allowed = {"low", "medium", "high"}
        if isinstance(v, str) and v.lower() not in allowed:
            raise ValueError(f"invalid priority '{v}', must be one of: low, medium, high")
        return v


class TodoPatch(BaseModel):
    title: Optional[str] = None
    checked: Optional[bool] = None
    priority: Optional[Priority] = None

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("title must be a non-empty string")
            if len(v.strip()) < 3:
                raise ValueError("title must be at least 3 characters long")
            return v.strip()
        return v

    @field_validator("priority", mode="before")
    @classmethod
    def priority_must_be_valid(cls, v):
        if v is not None:
            allowed = {"low", "medium", "high"}
            if isinstance(v, str) and v.lower() not in allowed:
                raise ValueError(f"invalid priority '{v}', must be one of: low, medium, high")
        return v


class TodoResponse(BaseModel):
    id: int
    title: str
    checked: bool
    priority: Priority


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        msg = error["msg"]
        messages.append(f"{field}: {msg}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": messages},
    )


def find_todo(todo_id: int):
    for index, todo in enumerate(todos_db):
        if todo["id"] == todo_id:
            return index, todo
    return None, None


@app.post("/todos", status_code=201, response_model=TodoResponse)
def create_todo(todo: TodoCreate):
    global id_counter
    id_counter += 1
    new_todo = {
        "id": id_counter,
        "title": todo.title,
        "checked": todo.checked,
        "priority": todo.priority.value,
    }
    todos_db.append(new_todo)
    return new_todo


@app.get("/todos", response_model=list[TodoResponse])
def get_all_todos(priority: Optional[Priority] = None, checked: Optional[bool] = None):
    filtered = todos_db

    if priority is not None:
        filtered = [t for t in filtered if t["priority"] == priority.value]

    if checked is not None:
        filtered = [t for t in filtered if t["checked"] == checked]

    return filtered


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    _, todo = find_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_data: TodoUpdate):
    index, existing = find_todo(todo_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")

    updated = {
        "id": todo_id,
        "title": todo_data.title,
        "checked": todo_data.checked,
        "priority": todo_data.priority.value,
    }
    todos_db[index] = updated
    return updated


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def partial_update_todo(todo_id: int, todo_data: TodoPatch):
    index, existing = find_todo(todo_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")

    if todo_data.title is not None:
        existing["title"] = todo_data.title
    if todo_data.checked is not None:
        existing["checked"] = todo_data.checked
    if todo_data.priority is not None:
        existing["priority"] = todo_data.priority.value

    todos_db[index] = existing
    return existing


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    index, todo = find_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    todos_db.pop(index)
    return {"message": f"Todo with id {todo_id} deleted successfully"}


@app.patch("/todos/{todo_id}/complete", response_model=TodoResponse)
def mark_todo_complete(todo_id: int):
    index, todo = find_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    todo["checked"] = True
    todos_db[index] = todo
    return todo
