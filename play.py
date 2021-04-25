#!/usr/bin/env python3
from game import SemiRandomBot, Table
from game.table.observer import TerminalJustPotCollectionTextualObserver
from game.player import TerminalPlayer

INIT_CHIPS = 10


def main():
    global INIT_CHIPS
    Table.INIT_CHIPS = INIT_CHIPS
    o = TerminalJustPotCollectionTextualObserver()
    t = Table([TerminalPlayer, SemiRandomBot, SemiRandomBot])
    t.attach_observer(o)
    t.run_tournament()


if __name__ == '__main__':
    main()
