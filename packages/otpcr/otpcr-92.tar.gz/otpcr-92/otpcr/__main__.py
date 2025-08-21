# This file is placed in the Public Domain.


"main"


import os
import pathlib
import sys
import time


from .auto   import Auto
from .client import Client
from .cmnd   import Commands, command, scan
from .event  import Event
from .parse  import parse
from .paths  import pidname, setwd
from .thread import launch
from .utils  import level, spl
from .       import modules as MODS


class Main(Auto):

    init = ""
    level = "warn"
    name = Auto.__module__.split(".")[-2]
    opts = Auto()
    verbose = False
    version = 92


class CLI(Client):

    def __init__(self):
        Client.__init__(self)
        self.register("command", command)

    def raw(self, txt):
        out(txt.encode('utf-8', 'replace').decode("utf-8"))


class Console(CLI):

    def announce(self, txt):
        pass

    def callback(self, event):
        super().callback(event)
        event.wait()

    def poll(self):
        evt = Event()
        evt.txt = input("> ")
        evt.type = "command"
        return evt


"daemon"


def daemon(verbose=False):
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    pid2 = os.fork()
    if pid2 != 0:
        os._exit(0)
    if not verbose:
        with open('/dev/null', 'r', encoding="utf-8") as sis:
            os.dup2(sis.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as sos:
            os.dup2(sos.fileno(), sys.stdout.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as ses:
            os.dup2(ses.fileno(), sys.stderr.fileno())
    os.umask(0)
    os.chdir("/")
    os.nice(10)


def pidfile(filename):
    if os.path.exists(filename):
        os.unlink(filename)
    path2 = pathlib.Path(filename)
    path2.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fds:
        fds.write(str(os.getpid()))


def privileges():
    import getpass
    import pwd
    pwnam2 = pwd.getpwnam(getpass.getuser())
    os.setgid(pwnam2.pw_gid)
    os.setuid(pwnam2.pw_uid)


"commands"


def ver(event):
    event.reply(f"{Main.name.upper()} {Main.version}")


"utilities"


def banner(mods):
    tme = time.ctime(time.time()).replace("  ", " ")
    out(f"{Main.name.upper()} {Main.version} since {tme} ({Main.level.upper()})")
    out(f"loaded {".".join(dir(mods))}")


def check(txt):
    args = sys.argv[1:]
    for arg in args:
        if not arg.startswith("-"):
            continue
        for char in txt:
            if char in arg:
                return True
    return False


def forever():
    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            print("")
            sys.exit(1)


def inits(pkg, names):
    modz = []
    for name in sorted(spl(names)):
        mod = getattr(pkg, name, None)
        if not mod:
            continue
        if "init" in dir(mod):
            thr = launch(mod.init)
            modz.append((mod, thr))
    return modz


def out(txt):
    print(txt)
    sys.stdout.flush()


"scripts"


def background():
    daemon("-v" in sys.argv)
    privileges()
    level(Main.level or "debug")
    setwd(Main.name)
    pidfile(pidname(Main.name))
    Commands.add(ver)
    scan(MODS)
    inits(MODS, Main.init or "irc,rss")
    forever()


def console():
    import readline # noqa: F401
    parse(Main, " ".join(sys.argv[1:]))
    Main.init = Main.sets.init or Main.init
    Main.verbose = Main.sets.verbose or Main.verbose
    Main.level   = Main.sets.level or Main.level or "warn"
    level(Main.level)
    setwd(Main.name)
    Commands.add(ver)
    scan(MODS)
    if "v" in Main.opts:
        banner(MODS)
    for _mod, thr in inits(MODS, Main.init):
        if "w" in Main.opts:
            thr.join(30.0)
    csl = Console()
    csl.start()
    forever()


def control():
    if len(sys.argv) == 1:
        return
    parse(Main, " ".join(sys.argv[1:]))
    level(Main.level or "warn")
    setwd(Main.name)
    Commands.scan(MODS.srv)
    Commands.add(ver)
    scan(MODS)
    csl = CLI()
    evt = Event()
    evt.orig = repr(csl)
    evt.type = "command"
    evt.txt = Main.otxt
    command(evt)
    evt.wait()


def service():
    level(Main.level or "warn")
    setwd(Main.name)
    banner(MODS)
    privileges()
    pidfile(pidname(Main.name))
    Commands.add(ver)
    scan(MODS)
    inits(MODS, Main.init or "irc,rss")
    forever()


"runtime"


def wrapped(func):
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        out("")


def wrap(func):
    import termios
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        wrapped(func)
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


def main():
    if check("a"):
        Main.init = ",".join(dir(MODS))
    if check("v"):
        setattr(Main.opts, "v", True)
    if check("c"):
        wrap(console)
    elif check("d"):
        background()
    elif check("s"):
        wrapped(service)
    else:
        wrapped(control)


if __name__ == "__main__":
    main()
