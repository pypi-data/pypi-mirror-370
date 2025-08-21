# This file is placed in the Public Domain.


"find"


import os
import time


from .disk   import Cache, read
from .object import Object, items, update
from .paths  import fqn, long, store


def find(clz, selector=None, deleted=False, matching=False):
    clz = long(clz)
    if selector is None:
        selector = {}
    for pth in fns(clz):
        obj = Cache.get(pth)
        if not obj:
            obj = Object()
            read(obj, pth)
            Cache.add(pth, obj)
        if not deleted and isdeleted(obj):
            continue
        if selector and not search(obj, selector, matching):
            continue
        yield pth, obj


def fns(clz):
    pth = store(clz)
    for rootdir, dirs, _files in os.walk(pth, topdown=False):
        for dname in dirs:
            ddd = os.path.join(rootdir, dname)
            for fll in os.listdir(ddd):
                yield os.path.join(ddd, fll)


def fntime(daystr):
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.replace("_", " ")
    if "." in datestr:
        datestr, rest = datestr.rsplit(".", 1)
    else:
        rest = ""
    timed = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    if rest:
        timed += float("." + rest)
    return float(timed)


def isdeleted(obj):
    return "__deleted__" in dir(obj) and obj.__deleted__


def last(obj, selector=None):
    if selector is None:
        selector = {}
    result = sorted(find(fqn(obj), selector), key=lambda x: fntime(x[0]))
    res = ""
    if result:
        inp = result[-1]
        update(obj, inp[-1])
        res = inp[0]
    return res


def search(obj, selector, matching=False):
    res = False
    if not selector:
        return res
    for key, value in items(selector):
        val = getattr(obj, key, None)
        if not val:
            continue
        if matching and value == val:
            res = True
        elif str(value).lower() in str(val).lower() or value == "match":
            res = True
        else:
            res = False
            break
    return res


def __dir__():
    return (
        'find',
        'fns',
        'fntime',
        'last',
        'search'
    )
