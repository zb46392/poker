#!/usr/bin/env python3
from game import SemiRandomBot, Table
from game.table.observer import TerminalTextualObserver, FileTextualObserver


def main():
    t = Table([SemiRandomBot, SemiRandomBot, SemiRandomBot])
    o = TerminalTextualObserver()
    f = FileTextualObserver()
    t.attach_observer(o)
    t.attach_observer(f)
    t.run_tournament()


if __name__ == '__main__':
    main()
