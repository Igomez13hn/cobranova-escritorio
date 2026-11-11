"""Cobranova office host. Serves the app and stores the book in SQLite."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = 8787


def app_dir() -> str:
    argv0 = os.path.dirname(os.path.abspath(sys.argv[0]))
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in (argv0, here):
        if os.path.isdir(os.path.join(candidate, "web")):
            return candidate
    return here


def web_dir() -> str:
    return os.path.join(app_dir(), "web")


def db_path() -> str:
    override = os.environ.get("COBRANOVA_DATA")
    if override:
        os.makedirs(override, exist_ok=True)
        return os.path.join(override, "libro.db")
    root = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".cobranova")
    folder = os.path.join(root, "Cobranova")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "libro.db")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(), check_same_thread=False)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS libro (id INTEGER PRIMARY KEY CHECK (id = 1), revision INTEGER NOT NULL, snapshot TEXT NOT NULL)"
    )
    return conn


DB = connect()
LOCK = threading.Lock()


def read_book() -> tuple[int, str | None]:
    with LOCK:
        row = DB.execute("SELECT revision, snapshot FROM libro WHERE id = 1").fetchone()
    if row is None:
        return 0, None
    return int(row[0]), str(row[1])


def write_book(snapshot: dict) -> int:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("settings"), dict):
        raise ValueError("libro invalido")
    for key in ("users", "clients", "loans", "movements", "receipts"):
        if not isinstance(snapshot.get(key), list):
            raise ValueError("libro invalido")
    payload = json.dumps(snapshot, ensure_ascii=False)
    with LOCK:
        current = DB.execute("SELECT revision FROM libro WHERE id = 1").fetchone()
        revision = 1 if current is None else int(current[0]) + 1
        DB.execute(
            "INSERT INTO libro (id, revision, snapshot) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET revision = excluded.revision, snapshot = excluded.snapshot",
            (revision, payload),
        )
        DB.commit()
    return revision


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def end(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/libro":
            revision, snapshot = read_book()
            if snapshot is None:
                body = {"ok": True, "empty": True, "revision": 0}
            else:
                body = {"ok": True, "empty": False, "revision": revision, "snapshot": json.loads(snapshot)}
            raw = json.dumps(body).encode("utf-8")
            self.end(200, raw, "application/json; charset=utf-8")
            return
        self.serve_file(path)

    def do_PUT(self) -> None:
        if self.path.split("?", 1)[0] != "/api/libro":
            self.end(404, b"{}", "application/json")
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > 20_000_000:
            self.end(400, b'{"ok":false}', "application/json")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            revision = write_book(payload.get("snapshot"))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.end(400, b'{"ok":false}', "application/json")
            return
        raw = json.dumps({"ok": True, "revision": revision}).encode("utf-8")
        self.end(200, raw, "application/json; charset=utf-8")

    def serve_file(self, path: str) -> None:
        root = os.path.realpath(web_dir())
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        target = os.path.realpath(os.path.join(root, rel))
        if not target.startswith(root) or not os.path.isfile(target):
            target = os.path.join(root, "index.html")
        ext = os.path.splitext(target)[1].lower()
        types = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".svg": "image/svg+xml",
            ".json": "application/json",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".png": "image/png",
            ".ico": "image/x-icon",
        }
        with open(target, "rb") as handle:
            data = handle.read()
        self.end(200, data, types.get(ext, "application/octet-stream"))


def main() -> None:
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        if os.environ.get("COBRANOVA_NO_BROWSER") != "1":
            webbrowser.open(f"http://127.0.0.1:{PORT}/")
        return
    if os.environ.get("COBRANOVA_NO_BROWSER") != "1":
        threading.Timer(0.6, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
