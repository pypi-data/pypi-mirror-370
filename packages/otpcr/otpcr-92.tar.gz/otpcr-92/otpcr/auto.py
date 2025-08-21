# This file is placed in the Public Domain.


"auto construct"


from .object import Object


class Auto(Object):

    def __getattr__(self, key):
        if key not in self:
            setattr(self, key, "")
        return self.__dict__.get(key, "")


def __dir__():
    return (
        'Auto',
    )
