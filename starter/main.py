# Starter file for Task C: Validation & Error Handling
# This is a working Todo CRUD API from Task B.
# Your task is to:
# 1. Replace `todo: dict` with a Pydantic model
# 2. Add proper validation (title, priority, checked)
# 3. Replace plain "not found" returns with proper HTTPException 404s
# 4. Return correct status codes (201 for create, 404 for not found, 400 for bad input)

from fastapi import FastAPI

app = FastAPI()

# Temporary in-memory storage
todos = []


@app.get("/")
def home():
    return {
        "message": "Todo API is running!"
    }


@app.get("/todos")
def get_todos():
    return todos


@app.post("/todos")
def create_todo(todo: dict):
    todos.append(todo)

    return {
        "message": "Todo added successfully"
    }


@app.get("/todos/{id}")
def get_todo(id: int):

    for todo in todos:
        if todo["id"] == id:
            return todo

    return {
        "message": "Todo not found"
    }


@app.put("/todos/{id}")
def update_todo(id: int, updated_todo: dict):

    for todo in todos:
        if todo["id"] == id:

            todo["title"] = updated_todo["title"]
            todo["checked"] = updated_todo["checked"]
            todo["priority"] = updated_todo["priority"]

            return {
                "message": "Todo updated successfully"
            }

    return {
        "message": "Todo not found"
    }


@app.delete("/todos/{id}")
def delete_todo(id: int):

    for todo in todos:
        if todo["id"] == id:

            todos.remove(todo)

            return {
                "message": "Todo deleted successfully"
            }

    return {
        "message": "Todo not found"
    }
