import sqlite3
import json
from typing import Optional, Dict

class Config():
    def __init__(self):
        self.conn = sqlite3.connect('musicbox.db')
        with self.conn:
            self.conn.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")

    def get(self, key: str, default=None):
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM config WHERE key=?", (key,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        else:
            return default

    def set(self, key: str, value) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )

