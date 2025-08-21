# This file is placed in the Public Domain.


"client pool"


import os
import threading


from .fleet  import Fleet
from .output import Output


class Pool:

    clients = []
    lock = threading.RLock()
    nrcpu = os.cpu_count()
    nrlast = 0

    @staticmethod
    def put(evt):
       with Pool.lock:
           if not Pool.clients:
               for task in range(Pool.nrcpu):
                   clt = Output()
                   clt.start()
               Pool.clients = list(Fleet.all())
           if Pool.nrlast >= Pool.nrcpu:
               Pool.nrlast = 0
           print(Pool.clients)
           Pool.clients[Pool.nrlast].put(evt)
           Pool.nrlast += 1


def __dir__():
    return (
        'Pool',
    )
