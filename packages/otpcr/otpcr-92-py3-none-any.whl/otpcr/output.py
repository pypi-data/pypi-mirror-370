# This file is placed in the Public Domain.


"output"


import queue
import threading


from .client import Client
from .thread import launch


class Output(Client):

    def __init__(self):
        Client.__init__(self)
        self.olock  = threading.RLock()
        self.oqueue = queue.Queue()
        self.ostop  = threading.Event()

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(event.channel, event.result[tme])

    def dosay(self, channel, txt):
        raise NotImplementedError("dosay")

    def oput(self, event):
        self.oqueue.put(event)

    def output(self):
        while not self.ostop.is_set():
            event = self.oqueue.get()
            if event is None:
                self.oqueue.task_done()
                break
            self.display(event)
            self.oqueue.task_done()

    def start(self):
        self.ostop.clear()
        launch(self.output)
        super().start()

    def stop(self):
        self.ostop.set()
        self.oqueue.put(None)
        super.stop()

    def wait(self):
        self.oqueue.join()


def __dir__():
    return (
        'Output',
    )
