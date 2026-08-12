from fastapi import FastAPI, HTTPException, Response, Request , Depends
from datetime import datetime
from random import randint 
from typing import Any , Annotated, TypeVar,Generic
from sqlmodel import SQLModel, create_engine, Session, Field, select
from contextlib import asynccontextmanager
from datetime import timezone
from pydantic import BaseModel


class Campaign(SQLModel, table = True):
    campaign_id: int | None = Field(default=None , primary_key = True)
    name: str = Field(index = True)
    due_date: datetime | None = Field(default=None , index=True)
    created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc), nullable=True, index=True) 


class campaignCreate(SQLModel):
    name: str
    due_date: datetime | None = None


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    with Session(engine) as session:
          if not session.exec(select(Campaign)).first():
              session.add_all([
                  Campaign(name="Summer Launch", due_date=datetime.now()),
                  Campaign(name="Good Day", due_date=datetime.now())
                             ])
              session.commit()
    yield

app = FastAPI(root_path="/api/v1" , lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello GOPAL JEE"}

data : Any = [
    {
        "campaign_id": 1,
        "name": "Summer Launch",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "campaign_id": 2,
        "name": "Good Day",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
]

"""
Campaigns
- campaign_id
- name
- due_date
- created_at
"""

T = TypeVar("T")
class Response(BaseModel, Generic[T]):
    data:T
class CampaignsResponse(BaseModel):
    Campaigns: list[Campaign]

@app.get("/campaigns" , response_model=Response[Campaign])
async def read_campaigns(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    return {"data":data}


@app.get("/campaigns/{id}" , response_model=Response[Campaign])
async def read_campaign(id: int, session:SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data": data}

@app.post("campaigns", status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign: campaignCreate, session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data":db_campaign}

@app.put("/campaign/{id}", response_model=Response[Campaign])
async def update_campaign(id: int , campaign: campaignCreate, session:SessionDep):
    data = session.get(campaign , id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}


@app.delete("/campaign/{id}", status_code=204)
async def delete_campaign(id: int , session:SessionDep):
      data = session.get(Campaign , id)
      if not data:
            raise HTTPException(status_code=404)
      session.delete(data)
      session.commit()





# @app.get("/campaigns")
# async def read_campaigns():
#     return {"campaigns": data}

# @app.get("/campaigns/{id}")
# async def read_campaigns(id: int):
#     for campaign in data:
#         if campaign.get("campaign_id") == id:
#             return {"campaign": campaign}
#         raise HTTPException(status_code=404)
# #POST KA CODE


# @app.post("/campaigns", status_code=201)
# async def create_campaigns(body: dict[str,Any]):
    

#     new : Any = {
#         "campaign_id": randint(100,1000),
#         "name": body.get("name"),
#         "due_date": body.get("due_date"),
#         "created_at": datetime.now()

#     }

#     data.append(new)
#     return {"campaigns": new}

# #PUT KA CODE

# @app.put("/campaign/{id}")
# async def update_campaign(id: int, body: dict[str, Any]):

#     for index, campaign in enumerate(data):
#         if campaign.get("campaign_id") == id:
#             upadated : Any = {
#                  "campaign_id": id,
#                  "name": body.get("name"),
#                  "due_date": body.get("due_date"),
#                  "created_at": campaign.get("created_at")
#             }

#             data[index] = upadated
#             return {"campaign": upadated}
#         raise HTTPException(status_code=404)


# @app.delete("/campaign/{id}")
# async def update_campaign(id: int):

#     for index, campaign in enumerate(data):
#         if campaign.get("campaign_id") == id:
#             data.pop(index)

#             return Response(status_code=204)
#         raise HTTPException(status_code=404)    

    
