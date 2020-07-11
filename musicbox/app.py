from json import dumps, loads

from sanic import Sanic
from sanic.response import json
from os.path import dirname, join

from .config import Config
from .cardreader import CardReader
from .music import Music
from .cards import Card, Cards

import soco

class App():
    config: Config
    card_reader: CardReader
    app: Sanic
    music: Music
    cards: Cards

    def __init__(self, card_reader, music):
        self.card_reader = card_reader
        self.config = Config()
        self.music = Music()
        self.cards = Cards()

        app = Sanic()
        self.app = app

        app.static("/", join(dirname(__file__), "public"))
        app.static("/", join(dirname(__file__), "public", "index.html"))

        @app.route("/test")
        async def test(request):
            return json({"hello": "world"})

        @app.route("/favorites")
        async def favorites(request):
            return json(self.music.favorites())

        @app.route("/playlists")
        async def playlists(request):
            return json(self.music.playlists())

        @app.route("/assign/<card_id:int>", methods=["PUT", "POST"])
        async def assign(request, card_id):
            card = self.cards.get(card_id)
            if not card:
                card = Card(card_id)
            print(request.json)
            card.update(**request.json)
            self.cards.store(card)
            return json({
                "card_id": card_id,
                **loads(card.json()),
            })

        @app.websocket("events")
        async def events(request, ws):
            async def event(card):
                body = {}

                if card:
                    metadata = self.cards.get(card)
                    if metadata:
                        body = {
                            "card_id": card,
                            **loads(metadata.json()),
                        }
                    else:
                        body = {"card_id": card}

                await ws.send(dumps(body))

            await event(card_reader.current)
            #await event(584194173067)
            queue = self.card_reader.subscribe()

            while ws:
                state, card = await queue.get()
                if state:
                    await event(card)
                else:
                    await event(None)

        @app.route("/discover")
        async def discover(request):
            zones = self.config.get("zones", [])

            return json([
                {
                    **speaker.get_speaker_info(),
                    "selected": bool(speaker.get_speaker_info()["serial_number"] in zones)
                }
                for speaker in soco.discover()
            ])

        @app.route("/zones", methods=["PUT", "POST"])
        async def set_zones(request):
            z = [
                    str(x) for x in request.json
            ]
            self.config.set("zones", z)
            print(request.json)
            return json({"zones": z})

