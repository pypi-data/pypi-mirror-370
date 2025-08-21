# This file is placed in the Public Domain.


"client"


import threading


from .fleet  import Fleet
from .engine import Engine


class Client(Engine):

    def __init__(self):
        Engine.__init__(self)
        self.olock = threading.RLock()
        Fleet.add(self)

    def announce(self, txt):
        pass

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(event.channel, event.result[tme])

    def dosay(self, channel, txt):
        self.say(channel, txt)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)


def __dir__():
    return (
        'Client',
    )
