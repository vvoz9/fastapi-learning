from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, UserRecord, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 学习项目启动时自动创建缺失的表，不会清空已有数据。
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


app = FastAPI(title="用户管理入门项目", lifespan=lifespan)


class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: str


class User(UserCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


@app.post("/users", response_model=User, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = UserRecord(name=data.name, email=data.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    return db.scalars(select(UserRecord).order_by(UserRecord.id)).all()


@app.get("/users/{id}", response_model=User)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.get(UserRecord, id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@app.put("/users/{id}", response_model=User)
def update_user(id: int, data: UserCreate, db: Session = Depends(get_db)):
    user = db.get(UserRecord, id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.name = data.name
    user.email = data.email
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.get(UserRecord, id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}
