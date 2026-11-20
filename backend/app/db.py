import os
import sqlite3
from contextlib import closing


def _run(sql: str, args=(), fetch=False):
    with closing(sqlite3.connect(os.getenv("DB_PATH", "app.db"))) as c:
        c.row_factory = sqlite3.Row
        with c:
            cur = c.execute(sql, args)
            return [dict(r) for r in cur.fetchall()] if fetch else None


def init():
    _run("CREATE TABLE IF NOT EXISTS history ("
         "id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, "
         "input TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")


def add(kind: str, text: str):
    _run("INSERT INTO history(kind, input) VALUES (?, ?)", (kind, text[:500]))


def recent(limit: int = 50):
    return _run("SELECT id, kind, input, created_at FROM history ORDER BY id DESC LIMIT ?",
                (limit,), fetch=True)


def clear():
    _run("DELETE FROM history")
