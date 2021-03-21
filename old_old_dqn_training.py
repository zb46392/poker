#!/usr/bin/env python3

from game import SemiRandomBot, SimpleDqnBot
from game import Table
from game.table.observer import TerminalObserver
from game.table.training_table import TrainingTable


def dqn_vs_semi_random() -> None:
    Table.INIT_CHIPS = 10
    t = TrainingTable([SimpleDqnBot, SemiRandomBot, SemiRandomBot])
    p = t._players._basic_player
    play(t=t, nbr_of_training=1_000_000, should_train=True)
    p.save_model()


def play(t: TrainingTable, ep: int = 10_000, nbr_of_games_to_print: int = 0, should_print_info: bool = True,
         nbr_of_training: int = 100_000, should_train: bool = False):
    if should_train:
        if should_print_info:
            print('Agent training...')
        play(t=t, ep=nbr_of_training, nbr_of_games_to_print=0, should_print_info=False,
             nbr_of_training=0, should_train=False)
        if should_print_info:
            print('Agent Finished training...')

    win_cnt = 0
    name = 'Player_1 (SimpleDqnBot)'
    for i in range(ep):
        print(f'\rEpisode: {i}/{ep}\t{round((100 / ep) * i, 2)}%', end='')
        t.reset()
        if i > (ep - (nbr_of_games_to_print + 1)):
            t.attach_observer(TerminalObserver())
        t.run_tournament()

        if t.get_winner() == name:
            win_cnt += 1

    print()
    if should_print_info:
        print(f'{name} has won {win_cnt} times.')


def main():
    dqn_vs_semi_random()


if __name__ == '__main__':
    main()
