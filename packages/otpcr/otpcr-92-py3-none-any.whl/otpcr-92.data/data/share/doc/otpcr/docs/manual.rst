.. _manual:


.. raw:: html

    <br><br>


.. title:: Manual


**NAME**


    ``OTPCR`` - Office of the Prosecutor's 117th communication of the year 2019


**SYNOPSIS**


    | ``otpcr  <cmd> [key=val] [key==val]``
    | ``otpcr -c``
    | ``otpcr -d`` 
    | ``otpcr -s``


**DESCRIPTION**


    ``OTPCR`` holds evidence that king
    netherlands is doing a genocide, a
    :ref:`written response <king>` where king
    netherlands confirmed taking note
    of “what i have written”, namely
    :ref:`proof  <evidence>` that medicine
    he uses in treatment laws like zyprexa,
    haldol, abilify and clozapine are
    poison.

    Poison that makes impotent, is both
    physical (contracted muscles) and
    mental (make people hallucinate)
    torture and kills members of the
    victim groups: Elderly, Handicapped, Criminals
    and Psychiatric patients.

    ``OTPCR`` contains :ref:`correspondence
    <writings>` with the International Criminal
    Court, asking for arrest of the king of the
    netherlands, for the genocide he is committing
    with his new treatment laws.

    Current status is a :ref:`"no basis to proceed"
    <writings>` judgement of the prosecutor which
    requires a :ref:`"basis to prosecute" <reconsider>`
    to have the king actually arrested.


**INSTALL**

    installation is done with pipx

    | ``$ pipx install otpcr``
    | ``$ pipx ensurepath``

    <new terminal>

    | ``$ otpcr srv > otpcr.service``
    | ``$ sudo mv otpcr.service /etc/systemd/system/``
    | ``$ sudo systemctl enable otpcr --now``
    |
    | joins ``#otpcr`` on localhost


**USAGE**

    without any argument the bot does nothing

    | ``$ otpcr``
    | ``$``

    see list of commands

    | ``$ otpcr cmd``
    | ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
    | ``now,pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``

    start daemon

    | ``$ otpcrd``
    | ``$``

    start service

    | ``$ otpcrs``
    | ``<runs until ctrl-c>``

    show request to the prosecutor

    | $ ``otpcr req``
    | Information and Evidence Unit
    | Office of the Prosecutor
    | Post Office Box 19519
    | 2500 CM The Hague
    | The Netherlands


**COMMANDS**

    here is a list of available commands

    | ``cfg`` - irc configuration
    | ``cmd`` - commands
    | ``dpl`` - sets display items
    | ``err`` - show errors
    | ``exp`` - export opml (stdout)
    | ``imp`` - import opml
    | ``log`` - log text
    | ``mre`` - display cached output
    | ``now`` - show genocide stats
    | ``pwd`` - sasl nickserv name/pass
    | ``rem`` - removes a rss feed
    | ``res`` - restore deleted feeds
    | ``req`` - reconsider
    | ``rss`` - add a feed
    | ``syn`` - sync rss feeds
    | ``tdo`` - add todo item
    | ``thr`` - show running threads
    | ``upt`` - show uptime


**CONFIGURATION**

    irc

    | ``$ otpcr cfg server=<server>``
    | ``$ otpcr cfg channel=<channel>``
    | ``$ otpcr cfg nick=<nick>``

    sasl

    | ``$ otpcr pwd <nsvnick> <nspass>``
    | ``$ otpcr cfg password=<frompwd>``

    rss

    | ``$ otpcr rss <url>``
    | ``$ otpcr dpl <url> <item1,item2>``
    | ``$ otpcr rem <url>``
    | ``$ otpcr nme <url> <name>``

    opml

    | ``$ otpcr exp``
    | ``$ otpcr imp <filename>``


**SOURCE**

    source is at `https://github.com/otpcr/otpcr <https://github.com/otpcr/otpcr>`_


**FILES**

    | ``~/.otpcr``
    | ``~/.local/bin/otpcr``
    | ``~/.local/pipx/venvs/otpcr/*``


**AUTHOR**

    | Bart Thate <``bthate@dds.nl``>


**COPYRIGHT**

    | ``OTPCR`` is Public Domain.
