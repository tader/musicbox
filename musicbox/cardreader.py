from typing import Set, Optional

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from asyncio import sleep, Queue

class CardReader():
    go: bool
    subscriptions: Set[Queue]
    current: Optional[int]

    def __init__(self):
        self.go = True
        self.subscriptions = set()
        self.current = None

    def stop(self):
        self.go = False

    def subscribe(self, ) -> Queue:
        queue = Queue(maxsize=10)
        self.subscriptions.add(queue)
        return queue

    def unsubscribe(self, queue) -> None:
        self.subscriptions.remove(queue)

    def fire(self, event) -> None:
        for queue in self.subscriptions:
            if queue.full():
                self.unsubscribe(subscription)
            else:
                queue.put_nowait(event)

    async def launch(self):
        self.go = True
        self.current = None
        gone_timer = 0

        while self.go:
            try:
                reader = SimpleMFRC522()

                while self.go:
                    id, text = reader.read_no_block()

                    if not id:
                        if self.current:
                            if gone_timer > 3:
                                self.fire((False, self.current))
                                self.current = None
                                gone_timer = 0
                            else:
                                gone_timer += 1

                    if id == self.current:
                        gone_timer = 0

                    if id and id != self.current:
                        self.current = id
                        self.fire((True, id))

                    await sleep(.1)
            finally:
                GPIO.cleanup()


