# This file is placed in the Public Domain.


"callback engine"


import queue
import threading


from .thread import launch


class Engine:

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()
        self.ready = threading.Event()
        self.stopped = threading.Event()

    def available(self, event):
        return event.type in self.cbs

    def callback(self, event):
        func = self.cbs.get(event.type, None)
        if func:
            event._thr = launch(func, event)

    def loop(self):
        while not self.stopped.is_set():
            event = self.poll()
            if event is None:
                break
            event.orig = repr(self)
            self.callback(event)

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put(event)

    def register(self, typ, cbs):
        self.cbs[typ] = cbs

    def start(self, daemon=True):
        self.stopped.clear()
        launch(self.loop, daemon=daemon)

    def stop(self):
        self.stopped.set()
        self.queue.put(None)

    def wait(self):
        pass


def __dir__():
    return (
        'Engine',
    )
