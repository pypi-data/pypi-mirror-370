from typing import Optional

from fastapi import Depends, FastAPI
from fastapi_fsp.fsp import FSPManager
from fastapi_fsp.models import PaginatedResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select


class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class HeroCreate(HeroBase):
    pass


class HeroPublic(HeroBase):
    id: int


class HeroUpdate(SQLModel):
    name: Optional[str] = None
    secret_name: Optional[str] = None
    age: Optional[int] = None


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def lifespan(app: FastAPI):
    create_db_and_tables()


app = FastAPI(lifespan=lifespan)


@app.get("/heroes/", response_model=PaginatedResponse[HeroPublic])
def read_heroes(*, session: Session = Depends(get_session), fsp: FSPManager = Depends(FSPManager)):
    heroes = select(Hero)
    return fsp.generate_response(heroes, session)
