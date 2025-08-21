# This file is placed in the Public Domain.


"show path to website"


import os


a = os.path.abspath
d = os.path.dirname
p = os.path.join


PATH = p(d(d(__file__)), "html", "index.html")


def pth(event):
    event.reply(f"file://localhost{PATH}")
