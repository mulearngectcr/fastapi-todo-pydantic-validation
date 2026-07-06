# Day 5 - Validated Todo API (Pydantic)

A FastAPI-based Todo API with comprehensive Pydantic validation and structured error handling, building upon the CRUD API from Day 4.

## Todo Model

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "checked": false,
  "priority": "medium"
}
```

## Endpoints

| Method   | Route                    | Description                 | Status Code |
| -------- | ------------------------ | --------------------------- | ----------- |
| `POST`   | `/todos`                 | Create a new todo           | 201         |
| `GET`    | `/todos`                 | Get all todos (filterable)  | 200         |
| `GET`    | `/todos/{id}`            | Get a single todo by ID     | 200 / 404   |
| `PUT`    | `/todos/{id}`            | Full update of a todo       | 200 / 404   |
| `PATCH`  | `/todos/{id}`            | Partial update of a todo    | 200 / 404   |
| `DELETE` | `/todos/{id}`            | Delete a todo               | 200 / 404   |
| `PATCH`  | `/todos/{id}/complete`   | Mark a todo as completed    | 200 / 404   |

### Query Filters on `GET /todos`

- `priority` — filter by `low`, `medium`, or `high`
- `checked` — filter by `true` or `false`

## Validation Rules

- **title** — must be a non-empty string with at least 3 characters
- **priority** — must be one of `low`, `medium`, or `high`
- **checked** — must be a boolean

## Error Handling

- `201` — returned on successful todo creation
- `400` — returned for invalid priority values
- `404` — returned when a todo with the given ID is not found
- `422` — returned with a custom message for missing or invalid fields

## Bonus Features

- Minimum length validation on `title` (3 characters)
- Custom 422 response for validation errors with field-level detail
- `PATCH /todos/{id}` endpoint for partial updates using an optional Pydantic model

## How to Run

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to test all endpoints via Swagger UI.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
