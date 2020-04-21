import asyncio
from .cardreader import CardReader
from .app import App
from .music import Music
from .cards import Cards

async def music(queue):
    cards = Cards()
    music = Music()

    while True:
        state, id = await queue.get()

        card = cards.get(id)

        if card:
            if state:
                print(f"enter {id}: {card.title}")
                music.play(card)
            else:
                print(f"exit {id}: {card.title}")
                music.pause(card)



async def run():
    card_reader = CardReader()
    launch_task = card_reader.launch()
    music_task = music(card_reader.subscribe())

    app = App(card_reader, music)
    server = await app.app.create_server(host="0.0.0.0", port=80, return_asyncio_server=True)
    await asyncio.gather(music_task, launch_task)


if __name__ == "__main__":
    asyncio.run(run())
