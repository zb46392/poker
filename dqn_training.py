#!/usr/bin/env python3

from game import SemiRandomBot, SimpleDqnBot, OpponentBotGold, OpponentBotSilver
from game import Table
from game.table.observer import TerminalObserver, FileObserver
from game.table.training_table import TrainingTable

NBR_OF_TRAINING = 0
NBR_OF_PRINT = 0
LOAD_MODEL_PATH = 'models/SimpleDqnBot_model_2020_09_20_19_27_49.weights'

ALPHA = 0.001
GAMMA = 0.999
EPSILON = 0.0
EPSILON_FLOOR = 0.1
SHOULD_EPSILON_DECAY = False
SHOULD_TRACK_PROGRESS = False
SHOULD_SAVE_MODEL_AFTER_TRAINING = False


def dqn_vs_semi_random() -> None:
    global NBR_OF_TRAINING, NBR_OF_PRINT, LOAD_MODEL_PATH, SHOULD_SAVE_MODEL_AFTER_TRAINING
    global ALPHA, GAMMA, EPSILON, EPSILON_FLOOR, SHOULD_EPSILON_DECAY, SHOULD_TRACK_PROGRESS

    Table.INIT_CHIPS = 10
    SimpleDqnBot.TRAIN_EPISODES = NBR_OF_TRAINING
    SimpleDqnBot.LOAD_MODEL = LOAD_MODEL_PATH
    SimpleDqnBot.ALPHA = ALPHA
    SimpleDqnBot.GAMMA = GAMMA
    SimpleDqnBot.EPSILON = EPSILON
    SimpleDqnBot.EPSILON_FLOOR = EPSILON_FLOOR
    SimpleDqnBot.SHOULD_EPSILON_DECAY = SHOULD_EPSILON_DECAY
    SimpleDqnBot.SHOULD_TRACK_PROGRESS = SHOULD_TRACK_PROGRESS
    SimpleDqnBot.SHOULD_SAVE_MODEL_AFTER_TRAINING = SHOULD_SAVE_MODEL_AFTER_TRAINING

    # t = TrainingTable([SimpleDqnBot, OpponentBotSilver, OpponentBotGold])
    t = TrainingTable([SimpleDqnBot, SemiRandomBot, SemiRandomBot])

    play(t=t, nbr_of_games_to_print=NBR_OF_PRINT, nbr_of_training=NBR_OF_TRAINING)


def play(t: TrainingTable, ep: int = 10_000, nbr_of_games_to_print: int = 2, should_print_info: bool = True,
         nbr_of_training: int = 100_000):
    if nbr_of_training > 0:
        if should_print_info:
            print('Agent training...')
        play(t=t, ep=nbr_of_training, nbr_of_games_to_print=0, should_print_info=False,
             nbr_of_training=0)
        if should_print_info:
            print('Agent Finished training...')

    win_cnt = {player_name: 0 for player_name in t.player_names}

    for i in range(ep):
        print(f'\rEpisode: {i}/{ep}\t{round((100 / ep) * i, 2)}%', end='')
        t.reset()

        to = None
        if i > (ep - (nbr_of_games_to_print + 1)):
            to = TerminalObserver()
            t.attach_observer(to)

        t.run_tournament()

        if to is not None:
            t.detach_observer(to)

        win_cnt[t.get_winner()] += 1

    print()
    if should_print_info:
        for name in win_cnt:
            print(f'{name} has won {win_cnt[name]} times.')


def main():
    dqn_vs_semi_random()


if __name__ == '__main__':
    main()
