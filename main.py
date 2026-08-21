# from fastapi import FastAPI, HTTPException, Response, Request , Depends
# from datetime import datetime
# from random import randint 
# from typing import Any , Annotated, TypeVar,Generic
# from sqlmodel import SQLModel, create_engine, Session, Field, select
# from contextlib import asynccontextmanager
# from datetime import timezone
# from pydantic import BaseModel


# class Campaign(SQLModel, table = True):
#     campaign_id: int | None = Field(default=None , primary_key = True)
#     name: str = Field(index = True)
#     due_date: datetime | None = Field(default=None , index=True)
#     created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc), nullable=True, index=True) 


# class campaignCreate(SQLModel):
#     name: str
#     due_date: datetime | None = None


# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args)

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

# def get_session():
#     with session(engine) as session:
#         yield session

# SessionDep = Annotated[Session, Depends(get_session)]

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     create_db_and_tables()

#     with Session(engine) as session:
#           if not session.exec(select(Campaign)).first():
#               session.add_all([
#                   Campaign(name="Summer Launch", due_date=datetime.now()),
#                   Campaign(name="Good Day", due_date=datetime.now())
#                              ])
#               session.commit()
#     yield

# app = FastAPI(root_path="/api/v1" , lifespan=lifespan)

# @app.get("/")
# async def root():
#     return {"message": "Hello GOPAL JEE"}

# data : Any = [
#     {
#         "campaign_id": 1,
#         "name": "Summer Launch",
#         "due_date": datetime.now(),
#         "created_at": datetime.now()
#     },
#     {
#         "campaign_id": 2,
#         "name": "Good Day",
#         "due_date": datetime.now(),
#         "created_at": datetime.now()
#     }
# ]

# """
# Campaigns
# - campaign_id
# - name
# - due_date
# - created_at
# """

# T = TypeVar("T")
# class Response(BaseModel, Generic[T]):
#     data:T
# class CampaignsResponse(BaseModel):
#     Campaigns: list[Campaign]

# @app.get("/campaigns" , response_model=Response[Campaign])
# async def read_campaigns(session: SessionDep):
#     data = session.exec(select(Campaign)).all()
#     return {"data":data}


# @app.get("/campaigns/{id}" , response_model=Response[Campaign])
# async def read_campaign(id: int, session:SessionDep):
#     data = session.get(Campaign, id)
#     if not data:
#         raise HTTPException(status_code=404)
#     return {"data": data}

# @app.post("campaigns", status_code=201, response_model=Response[Campaign])
# async def create_campaign(campaign: campaignCreate, session: SessionDep):
#     db_campaign = Campaign.model_validate(campaign)
#     session.add(db_campaign)
#     session.commit()
#     session.refresh(db_campaign)
#     return {"data":db_campaign}

# @app.put("/campaign/{id}", response_model=Response[Campaign])
# async def update_campaign(id: int , campaign: campaignCreate, session:SessionDep):
#     data = session.get(campaign , id)
#     if not data:
#         raise HTTPException(status_code=404)
#     data.name = campaign.name
#     data.due_date = campaign.due_date
#     session.add(data)
#     session.commit()
#     session.refresh(data)
#     return {"data":data}


# @app.delete("/campaign/{id}", status_code=204)
# async def delete_campaign(id: int , session:SessionDep):
#       data = session.get(Campaign , id)
#       if not data:
#             raise HTTPException(status_code=404)
#       session.delete(data)
#       session.commit()





# # @app.get("/campaigns")
# # async def read_campaigns():
# #     return {"campaigns": data}

# # @app.get("/campaigns/{id}")
# # async def read_campaigns(id: int):
# #     for campaign in data:
# #         if campaign.get("campaign_id") == id:
# #             return {"campaign": campaign}
# #         raise HTTPException(status_code=404)
# # #POST KA CODE


# # @app.post("/campaigns", status_code=201)
# # async def create_campaigns(body: dict[str,Any]):
    

# #     new : Any = {
# #         "campaign_id": randint(100,1000),
# #         "name": body.get("name"),
# #         "due_date": body.get("due_date"),
# #         "created_at": datetime.now()

# #     }

# #     data.append(new)
# #     return {"campaigns": new}

# # #PUT KA CODE

# # @app.put("/campaign/{id}")
# # async def update_campaign(id: int, body: dict[str, Any]):

# #     for index, campaign in enumerate(data):
# #         if campaign.get("campaign_id") == id:
# #             upadated : Any = {
# #                  "campaign_id": id,
# #                  "name": body.get("name"),
# #                  "due_date": body.get("due_date"),
# #                  "created_at": campaign.get("created_at")
# #             }

# #             data[index] = upadated
# #             return {"campaign": upadated}
# #         raise HTTPException(status_code=404)


# # @app.delete("/campaign/{id}")
# # async def update_campaign(id: int):

# #     for index, campaign in enumerate(data):
# #         if campaign.get("campaign_id") == id:
# #             data.pop(index)

# #             return Response(status_code=204)
# #         raise HTTPException(status_code=404)    


from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import get_connection, init_db, SEED_TASKS

app = FastAPI(title="Task API", version="1.0")


class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.on_event("startup")
def on_startup():
    # Stage 0: create the database/table and seed it if empty.
    init_db()


def row_to_task(row) -> dict:
    """Map a sqlite Row to the same task shape the API has always returned."""
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.get("/", summary="API info")
def read_root():
    """Basic info about this API and its main endpoint."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health_check():
    """Returns ok if the server is alive."""
    return {"status": "ok"}


@app.get("/tasks", summary="List tasks (with optional filters)")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    """Returns tasks, optionally filtered by done status or a title search term."""
    # Stage 1: reads now go through SQL instead of the in-memory list.
    query = "SELECT id, title, done FROM tasks"
    clauses = []
    params: list = []

    if done is not None:
        clauses.append("done = ?")
        params.append(1 if done else 0)
    if search is not None:
        # Optional extra: SQL LIKE search, case-insensitive.
        clauses.append("title LIKE ? COLLATE NOCASE")
        params.append(f"%{search}%")

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    return [row_to_task(r) for r in rows]


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Returns a single task by id, or 404 if it doesn't exist."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row_to_task(row)


@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(payload: TaskCreate):
    """Creates a new task. title is required and cannot be empty."""
    # Stage 2: inserts now go through SQL instead of appending to an array.
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0)", (payload.title,)
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (new_id,)
        ).fetchone()
    finally:
        conn.close()

    return row_to_task(row)


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """Updates a task's title and/or done status. 404 if the id doesn't exist."""
    # Stage 3: updates now go through SQL.
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        new_title = existing["title"]
        if payload.title is not None:
            if not payload.title.strip():
                raise HTTPException(status_code=400, detail="title cannot be empty")
            new_title = payload.title

        new_done = existing["done"]
        if payload.done is not None:
            new_done = 1 if payload.done else 0

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id),
        )
        conn.commit()

        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    finally:
        conn.close()

    return row_to_task(row)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Deletes a task by id. 404 if it doesn't exist."""
    # Stage 3: deletes now go through SQL.
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    finally:
        conn.close()
    return


@app.get("/stats", summary="Task stats")
def get_stats():
    """Returns total, done, and open task counts."""
    # Optional extra: computed with SQL COUNT() instead of counting in Python.
    conn = get_connection()
    try:
        total, done_count = conn.execute(
            "SELECT COUNT(*), SUM(done) FROM tasks"
        ).fetchone()
    finally:
        conn.close()

    done_count = done_count or 0
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/reset", summary="Reset to seed data")
def reset_tasks():
    """Restores the 3 example tasks. Handy for demos."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'tasks'")
        conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "reset"}

    
