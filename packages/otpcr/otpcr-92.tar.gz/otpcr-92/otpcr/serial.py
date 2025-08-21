# This file is placed in the Public Domain.


"decoder/encoder"


import json


from .object import Object, construct


class Encoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if issubclass(type(o), Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


def dump(obj, fp, *args, **kw):
    kw["cls"] = Encoder
    json.dump(obj, fp, *args, **kw)


def dumps(obj, *args, **kw):
    kw["cls"] = Encoder
    return json.dumps(obj, *args, **kw)


def hook(objdict):
    obj = Object()
    construct(obj, objdict)
    return obj


def load(fp, *args, **kw):
    kw["object_hook"] = hook
    return json.load(fp, *args, **kw)


def loads(s, *args, **kw):
    kw["object_hook"] = hook
    return json.loads(s, *args, **kw)


def __dir__():
    return (
       'dump',
       'dumps',
       'load',
       'loads'
    )
