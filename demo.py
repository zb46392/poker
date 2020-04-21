#!/usr/bin/env python3
from game import Dummy, RandomBot, SemiRandomBot
from game import Table
from game.table.observer import TerminalObserver, FileObserver


def main():
    t = Table([SemiRandomBot, SemiRandomBot, SemiRandomBot])
    o = TerminalObserver()
    f = FileObserver()
    t.attach_observer(o)
    t.attach_observer(f)
    t.run_tournament()


if __name__ == '__main__':
    main()
