# This file is placed in the Public Domain.


"command"


import inspect


from .fleet  import Fleet
from .parse  import parse


class Commands:

    cmds = {}
    names = {}

    @staticmethod
    def add(func, mod=None):
        Commands.cmds[func.__name__] = func
        if mod:
            Commands.names[func.__name__] = mod.__name__.split(".")[-1]

    @staticmethod
    def get(cmd):
        return Commands.cmds.get(cmd, None)

    @staticmethod
    def scan(mod):
        for key, cmdz in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if "event" in cmdz.__code__.co_varnames:
                Commands.add(cmdz, mod)


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def scan(pkg):
    mods = []
    for modname in dir(pkg):
        mod = getattr(pkg, modname)
        Commands.scan(mod)
        mods.append(mod)
    return mods


def __dir__():
    return (
        'Commands',
        'command',
        'scan'
    )
