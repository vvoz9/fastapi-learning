"""真实 HTTP + PostgreSQL 测试，包含应用重启和测试数据清理。"""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4


class UserAPITest(unittest.TestCase):
    def request(self, method, path, data=None):
        body = None if data is None else json.dumps(data).encode()
        req = Request(self.base + path, data=body, method=method,
                      headers={"Content-Type": "application/json"})
        try:
            response = urlopen(req, timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def start_server(self):
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1",
             "--port", str(self.port)], cwd=Path(__file__).parent)
        for _ in range(100):
            if self.process.poll() is not None:
                self.fail("应用启动失败，请检查 PostgreSQL 和 .env")
            try:
                if self.request("GET", "/users")[0] == 200:
                    return
            except (URLError, TimeoutError):
                pass
            time.sleep(0.1)
        self.fail("应用启动超时")

    def stop_server(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=10)

    def test_crud_and_restart(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        self.base = f"http://127.0.0.1:{self.port}"
        self.process = None
        user_id = None
        try:
            self.start_server()
            data = {"name": "测试用户", "email": f"test-{uuid4().hex}@example.com"}
            status, user = self.request("POST", "/users", data)
            self.assertEqual(status, 201)
            user_id = user["id"]
            self.assertEqual(user, {"id": user_id, **data})
            path = f"/users/{user_id}"
            self.assertEqual(self.request("GET", path), (200, user))
            status, users = self.request("GET", "/users")
            self.assertEqual(status, 200)
            self.assertIn(user, users)
            changed = {"name": "修改后的用户", "email": f"updated-{uuid4().hex}@example.com"}
            expected = {"id": user_id, **changed}
            self.assertEqual(self.request("PUT", path, changed), (200, expected))
            self.assertEqual(self.request("GET", path), (200, expected))
            self.assertEqual(self.request("POST", "/users", {"name": "缺少邮箱"})[0], 422)
            self.assertEqual(self.request("PUT", path, {"name": "", "email": "x"})[0], 422)
            self.stop_server()
            self.start_server()
            self.assertEqual(self.request("GET", path), (200, expected))
            print("PASS: user and updated fields survived application restart.")
            self.assertEqual(self.request("DELETE", path)[0], 200)
            self.assertEqual(self.request("GET", path)[0], 404)
            self.assertEqual(self.request("PUT", path, changed)[0], 404)
            self.assertEqual(self.request("DELETE", path)[0], 404)
            self.assertNotIn(user_id, [u["id"] for u in self.request("GET", "/users")[1]])
            user_id = None
            print("PASS: all five endpoints, validation and missing-user responses.")
        finally:
            try:
                if user_id is not None and self.process is not None and self.process.poll() is None:
                    self.request("DELETE", f"/users/{user_id}")
            finally:
                self.stop_server()


if __name__ == "__main__":
    unittest.main()
