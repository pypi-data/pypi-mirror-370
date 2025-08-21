# This file is placed in the Public Domain.


"threads"


import logging
import queue
import time
import threading
import _thread


lock = threading.RLock()


class Thread(threading.Thread):

    def __init__(self, func, thrname, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, thrname, (), daemon=daemon)
        self.name = thrname or kwargs.get("name", name(func))
        self.queue = queue.Queue()
        self.result = None
        self.starttime = time.time()
        self.stopped = threading.Event()
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

    def run(self):
        func, args = self.queue.get()
        try:
            self.result = func(*args)
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()

    def join(self, timeout=None):
        super().join(timeout)
        return self.result


def launch(func, *args, **kwargs):
    with lock:
        thread = Thread(func, None, *args, **kwargs)
        thread.start()
        return thread


def name(obj):
    typ = type(obj)
    if "__builtins__" in dir(typ):
        return obj.__name__
    if "__self__" in dir(obj):
        return f"{obj.__self__.__class__.__name__}.{obj.__name__}"
    if "__class__" in dir(obj) and "__name__" in dir(obj):
        return f"{obj.__class__.__name__}.{obj.__name__}"
    if "__class__" in dir(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    if "__name__" in dir(obj):
        return f"{obj.__class__.__name__}.{obj.__name__}"
    return ""


def __dir__():
    return (
        'Thread',
        'launch',
        'name'
    )
