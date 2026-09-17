# FastAPI 用户管理入门项目

需要 Python 3.10 或更高版本。在项目目录运行（Windows PowerShell）：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

打开 http://127.0.0.1:8000/docs，在交互文档中点击 **Try it out** 测试接口。
按 `Ctrl+C` 停止服务。

| 接口 | 作用 |
| --- | --- |
| POST /users | 创建用户，自动生成 id，返回 201 |
| GET /users | 获取全部用户 |
| GET /users/{id} | 按 id 获取用户，不存在返回 404 |
| DELETE /users/{id} | 按 id 删除用户，不存在返回 404 |

创建用户时的 JSON 请求体：

```json
{"name": "小明", "email": "xiaoming@example.com"}
```

`name` 和 `email` 都是必填字符串，`name` 不可为空。当前不校验邮箱格式。
`id` 由服务端递增生成。数据保存在 Python 字典里，重启（含自动重载）后清空。
这是单进程学习示例，请勿使用多个 worker。

文件说明：`main.py` 包含数据模型、内存数据和四个接口；
`requirements.txt` 列出依赖；`.gitignore` 排除虚拟环境和缓存。
