import sqlite3
import json
from typing import Optional, Dict

class Card():
    id: int
    title: Optional[str]
    content_type: Optional[str]
    content_id: Optional[int]
    shuffle: bool

    def __init__(self, id):
        self.id = id
        self.title = None
        self.content_type = None
        self.content_id = None
        self.shuffle = False

    def json(self) -> str:
        return json.dumps({
            "title": self.title,
            "content_type": self.content_type,
            "content_id": self.content_id,
            "shuffle": self.shuffle,
        })

    @classmethod
    def load(cls, id: int, text: str) -> "Card":
        d = json.loads(text)
        card = Card(id)
        card.update_from_json(text)
        return card

    def update_from_json(self, text: str) -> None:
        self.update(**json.loads(text))

    def update(self, **data) -> None:
        if "playlist" in data:
            self.content_id = data["playlist"]
            self.content_type = "sonos.playlist"

        for k in ("title", "content_type", "content_id", "shuffle"):
            if k in data:
                setattr(self, k, data[k])


class Cards():
    def __init__(self):
        self.conn = sqlite3.connect('musicbox.db')
        with self.conn:
            self.conn.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, metadata TEXT)")

    def get(self, card_id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, metadata FROM card WHERE id=?", (card_id,))
        row = cur.fetchone()
        if row:
            return Card.load(*row)
        else:
            return Card(card_id)

    def store(self, card:Card) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO card (id, metadata) VALUES (?, ?)",
                (card.id, card.json())
            )

