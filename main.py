from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="用户管理入门项目")


class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: str


class User(UserCreate):
    id: int


# 数据只保存在内存中，重启服务后会清空。
users: dict[int, User] = {}
next_id = 1


@app.post("/users", response_model=User, status_code=201)
def create_user(data: UserCreate):
    global next_id
    user = User(id=next_id, name=data.name, email=data.email)
    users[user.id] = user
    next_id += 1
    return user


@app.get("/users", response_model=list[User])
def get_users():
    return list(users.values())


@app.get("/users/{id}", response_model=User)
def get_user(id: int):
    if id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    return users[id]


@app.delete("/users/{id}")
def delete_user(id: int):
    if id not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    del users[id]
    return {"message": "用户已删除"}
