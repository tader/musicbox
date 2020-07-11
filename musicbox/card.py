import json
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class Card():
    card_id: int
    title: Optional[str] = None
    content_type: Optional[str] = None
    content_id: Optional[int] = None
    shuffle: bool = False

    def json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def load(cls, card_id: int, text: str) -> "Card":
        card = Card(card_id=card_id)
        card.update_from_json(text)
        return card

    def update_from_json(self, text: str) -> None:
        self.update(**json.loads(text))

    def update(self, **data) -> None:
        for k in self.__dict__.keys():
            if k in data:
                setattr(self, k, data[k])

