# This file is placed in the Public Domain.


"debug"


import time


from ..client import Fleet


def dbg(event):
    event.reply("raising exception")
    raise Exception("yo!")


def brk(event):
    event.reply("borking")
    for clt in Fleet.all():
        if "sock" in dir(clt):
            event.reply(f"shutdown on {clt.cfg.server}")
            time.sleep(2.0)
            try:
                clt.sock.shutdown(2)
            except OSError:
                pass
