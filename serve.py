# -*- coding: utf-8 -*-
"""每日一练题库本地服务：静态文件 + 错题/收藏写接口。
启动：python serve.py （默认 8123，仅绑定 127.0.0.1）
接口：POST /api/flaw   body=错题json  -> 写 userdata/flaw.json
      POST /api/favor  body=收藏json  -> 写 userdata/favor.json
      POST /api/proc   body=进度json  -> 写 userdata/proc.json
"""
import json, os, re, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "userdata")

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")   # 本地开发服务禁用缓存，杜绝旧列表/旧页面
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/list":
            """自动发现题库：列出 question/ 下全部 .json 文件"""
            try:
                qdir = os.path.join(ROOT, "question")
                files = sorted(f for f in os.listdir(qdir) if f.endswith(".json"))
            except Exception:
                files = []
            body = json.dumps(files).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def _json_response(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_import(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            self._json_response(400, {"message": "bad json"}); return
        fn = str(payload.get("filename", ""))
        data = payload.get("data")
        if not re.match(r"^[\w()（）\-]+\.json$", fn):
            self._json_response(400, {"message": "文件名不合法"}); return
        if not isinstance(data, dict) or not isinstance(data.get("name"), str) \
                or not isinstance(data.get("questions"), list) or not data["questions"]:
            self._json_response(400, {"message": "题库结构不完整"}); return
        ids = [q.get("id") for q in data["questions"]]
        if not all(ids) or len(set(ids)) != len(ids):
            self._json_response(400, {"message": "ID 缺失或重复"}); return
        dst = os.path.join(ROOT, "question", fn)
        if os.path.exists(dst):
            self._json_response(409, {"message": "同名题库已存在，请换一个名称"}); return
        tmp = dst + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, dst)
        self._json_response(200, {"ok": 1})

    def _handle_bank(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            self._json_response(400, {"message": "bad json"}); return
        fn = str(payload.get("filename", ""))
        data = payload.get("data")
        if not re.match(r"^[\w()（）\-]+\.json$", fn):
            self._json_response(400, {"message": "文件名不合法"}); return
        dst = os.path.join(ROOT, "question", fn)
        if not os.path.isfile(dst):
            self._json_response(404, {"message": "题库不存在"}); return
        if not isinstance(data, dict) or not isinstance(data.get("name"), str) or not data["name"].strip() \
                or not isinstance(data.get("questions"), list) or not data["questions"]:
            self._json_response(400, {"message": "题库结构不完整"}); return
        ids = [q.get("id") for q in data["questions"]]
        if not all(ids) or len(set(ids)) != len(ids):
            self._json_response(400, {"message": "ID 缺失或重复"}); return
        tmp = dst + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, dst)
        self._json_response(200, {"ok": 1})

    def do_POST(self):
        if self.path == "/api/import":
            return self._handle_import()
        if self.path == "/api/bank":
            return self._handle_bank()
        API_MAP = {"/api/flaw": "flaw.json", "/api/favor": "favor.json",
                   "/api/proc": "proc.json", "/api/ui": "ui.json"}
        if self.path not in API_MAP:
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            self.send_error(400, "bad json")
            return
        if not isinstance(data, dict):
            self.send_error(400, "bad structure")
            return
        if self.path not in ("/api/proc", "/api/ui") and "questions" not in data:
            self.send_error(400, "bad structure")
            return
        fn = API_MAP[self.path]
        os.makedirs(DATA, exist_ok=True)   # 用户手动删除 userdata 时自动重建
        tmp = os.path.join(DATA, fn + ".tmp")
        dst = os.path.join(DATA, fn)
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            os.replace(tmp, dst)
        except Exception as e:
            self.send_error(500, str(e))
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":1}')

if __name__ == "__main__":
    os.chdir(ROOT)   # 静态文件与 API 同根：从任意目录启动都能正常服务
    os.makedirs(DATA, exist_ok=True)
    port = 8123
    print("serving %s on http://127.0.0.1:%d" % (ROOT, port))
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
