from uuid import UUID, uuid4
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

# ----------------------------
# Models
# ----------------------------

class Todo(BaseModel):
    tid: UUID = Field(default_factory=uuid4)
    title: str = Field(..., min_length=3, max_length=100)
    checked: bool = False
    priority: str


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    checked: Optional[bool] = None
    priority: Optional[str] = None


# ----------------------------
# In-memory Database
# ----------------------------

all_todos: List[Todo] = []

ALLOWED_PRIORITIES = ["low", "medium", "high"]


# ----------------------------
# Custom Validation Error
# ----------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    missing_fields = [
        error["loc"][-1]
        for error in exc.errors()
        if error["type"] == "missing"
    ]

    if missing_fields:
        return JSONResponse(
            status_code=422,
            content={
                "message": "Required fields are missing.",
                "missing_fields": missing_fields
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation failed.",
            "errors": exc.errors()
        }
    )


# ----------------------------
# GET All Todos
# ----------------------------

@app.get("/todos")
async def get_todos(
    priority: Optional[str] = None,
    checked: Optional[bool] = None,
):
    todos = all_todos

    if priority is not None:
        todos = [todo for todo in todos if todo.priority == priority]

    if checked is not None:
        todos = [todo for todo in todos if todo.checked == checked]

    return todos


# ----------------------------
# GET Todo by ID
# ----------------------------

@app.get("/todos/{todo_id}")
async def get_todo(todo_id: UUID):

    for todo in all_todos:
        if todo.tid == todo_id:
            return todo

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


# ----------------------------
# CREATE Todo
# ----------------------------

@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo):

    if todo.priority not in ALLOWED_PRIORITIES:
        raise HTTPException(
            status_code=400,
            detail="Priority must be low, medium, or high."
        )

    all_todos.append(todo)
    return todo


# ----------------------------
# UPDATE Todo
# ----------------------------

@app.put("/todos/{todo_id}")
async def update_todo(todo_id: UUID, todo: Todo):

    if todo.priority not in ALLOWED_PRIORITIES:
        raise HTTPException(
            status_code=400,
            detail="Priority must be low, medium, or high."
        )

    for index, existing_todo in enumerate(all_todos):
        if existing_todo.tid == todo_id:
            todo.tid = todo_id
            all_todos[index] = todo
            return todo

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


# ----------------------------
# PATCH Todo
# ----------------------------

@app.patch("/todos/{todo_id}")
async def patch_todo(todo_id: UUID, updates: TodoUpdate):

    for todo in all_todos:

        if todo.tid == todo_id:

            if updates.title is not None:
                todo.title = updates.title

            if updates.checked is not None:
                todo.checked = updates.checked

            if updates.priority is not None:

                if updates.priority not in ALLOWED_PRIORITIES:
                    raise HTTPException(
                        status_code=400,
                        detail="Priority must be low, medium, or high."
                    )

                todo.priority = updates.priority

            return todo

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


# ----------------------------
# DELETE Todo
# ----------------------------

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: UUID):

    for index, todo in enumerate(all_todos):

        if todo.tid == todo_id:
            return all_todos.pop(index)

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )