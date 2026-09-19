# FastAPI + PostgreSQL 用户管理

简单学习项目：FastAPI 处理请求，Pydantic 校验输入，SQLAlchemy ORM 读写 PostgreSQL。
用户只有 `id`、`name`、`email` 三个字段，不再使用内存字典。

## 在当前电脑启动

本机 PostgreSQL 安装及数据位于 `%LOCALAPPDATA%\fastapi-learning-postgres`，
不依赖 Docker，不随 Git 提交。电脑重启后，在项目目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\start-db.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

本地 `.env` 已配置随机密码。不要提交或分享这个文件。
访问 http://127.0.0.1:8000/docs ，点击 **Try it out** 测试接口；`Ctrl+C` 停止应用。
应用启动时自动创建缺失的 `users` 表，重启应用不会删除数据。
本机 PostgreSQL 使用 EDB 的 Windows 二进制包：https://www.enterprisedb.com/download-postgresql-binaries

## 在其他电脑配置

需要 Python 3.10+ 和 PostgreSQL。可使用自己安装的 PostgreSQL，创建用户及数据库，
或启动 Docker Desktop 后使用项目的 Compose：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# 先编辑 .env，把示例密码替换为自己的密码，再启动数据库。
docker compose up -d --wait
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

`.env` 包含数据库主机、端口、数据库名、用户名和密码；`.env.example` 只有示例值。
本机 PostgreSQL 与 Docker 方案二选一，避免占用相同端口。
Docker 数据保存在命名卷中，`docker compose down` 保留数据，`down -v` 会删除数据。
已有数据库使用自己的连接配置，无需启动 Compose。
本次实测使用本机 PostgreSQL；Docker 引擎因 socket 文件访问错误未能启动，Compose 方案未实测。

## 接口

| 接口 | 作用 |
| --- | --- |
| POST /users | 创建用户，数据库自动生成 id，返回 201 |
| GET /users | 查询全部用户，按 id 排序 |
| GET /users/{id} | 查询单个用户 |
| PUT /users/{id} | 修改用户，需同时提交 name 和 email |
| DELETE /users/{id} | 删除用户，返回 200 和提示消息 |

创建和修改时使用 JSON：

```json
{"name": "小明", "email": "xiaoming@example.com"}
```

`name` 和 `email` 必须是字符串，`name` 不可为空；暂不校验邮箱格式或唯一性。
用户不存在返回 404，输入不符合要求返回 422。原内存版的数据不会自动迁移。

## 运行真实数据库测试

先启动 PostgreSQL，再运行：

```powershell
.\.venv\Scripts\python.exe test_api.py
```

测试会在空闲端口启动真实 Uvicorn 服务，通过 HTTP 测试创建、列表、单个查询、修改、
删除、422 和 404，并停止、重新启动应用，确认修改后的用户仍存在。
只清理自己创建的测试用户，不清空表；无需另装测试框架。
2026-09-19 本机 PostgreSQL 17.11 实测通过，应用重启后用户及修改后的字段均保留。

## 文件说明

- `main.py`：Pydantic 输入输出模型、五个接口、启动时建表。
- `database.py`：加载 `.env`、数据库连接、Session 和用户 ORM 表模型。
- `.env`：本机真实连接配置（Git 忽略）。
- `.env.example`：可提交的配置模板。
- `start-db.ps1`：启动当前电脑已安装的 PostgreSQL。
- `compose.yaml`：其他电脑可选的 PostgreSQL 容器及持久化卷配置。
- `test_api.py`：真实接口和应用重启持久性测试。
- `requirements.txt`：Python 依赖。
- `.gitignore`：忽略密码配置、虚拟环境及 Python 缓存。

这是学习示例，暂不包含登录权限或数据库迁移工具。
`create_all` 只创建缺失的表，不会自动修改已有表结构。
