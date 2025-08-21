# This file is placed in the Public Domain.


"fleet"


import time


class Fleet:

    clients = {}

    @staticmethod
    def add(client):
        Fleet.clients[repr(client)] = client

    @staticmethod
    def all():
        return Fleet.clients.values()

    @staticmethod
    def announce(txt):
        for client in Fleet.all():
            client.announce(txt)

    @staticmethod
    def dispatch(evt):
        client = Fleet.get(evt.orig)
        client.put(evt)

    @staticmethod
    def display(evt):
        client = Fleet.get(evt.orig)
        client.display(evt)

    @staticmethod
    def first():
        clt = list(Fleet.all())
        res = None
        if clt:
            res = clt[0]
        return res

    @staticmethod
    def get(orig):
        return Fleet.clients.get(orig, None)

    @staticmethod
    def say(orig, channel, txt):
        client = Fleet.get(orig)
        if client:
            client.say(channel, txt)

    @staticmethod
    def shutdown():
        for client in Fleet.all():
            client.stop()

    @staticmethod
    def wait():
        time.sleep(0.1)
        for client in Fleet.all():
            client.wait()


def __dir__():
    return (
        'Fleet',
    )
