#!/usr/bin/env python3

from game import SemiRandomBot, SimpleDqnBot, OpponentBotGold, OpponentBotSilver
from game import Table, TrainingTable
from game.table.observer import TerminalObserver, FileObserver
from game.player import Mode as PlayerMode
from game.player.dqn import NeuralNetwork
from game.player.monitor import MonitoredSimpleDqnBot

ALPHA = 0.0001
GAMMA = 0.999
EPSILON = 1.0
EPSILON_FLOOR = 0.1
SHOULD_EPSILON_DECAY = True
TRAINING_EPISODES_AMOUNT = 1_000_000
VALIDATION_EPISODES_AMOUNT = 100
VALIDATION_AMOUNT = 100
# LOAD_MODEL_PATH = 'models/SimpleDqnBot_model_2020_09_20_19_27_49.weights'
LOAD_MODEL_PATH = None
SHOULD_SAVE_MODEL = False
INIT_CHIPS = 10


def play():
    global TRAINING_EPISODES_AMOUNT, VALIDATION_EPISODES_AMOUNT, VALIDATION_AMOUNT, INIT_CHIPS, SHOULD_SAVE_MODEL
    validation_frequency = TRAINING_EPISODES_AMOUNT + 1
    if VALIDATION_AMOUNT > 0:
        validation_frequency = TRAINING_EPISODES_AMOUNT / VALIDATION_AMOUNT
    Table.INIT_CHIPS = INIT_CHIPS

    prepare_dqn()
    prepare_monitored_dqn()
    table = TrainingTable([MonitoredSimpleDqnBot, SemiRandomBot, SemiRandomBot])
    monitored_player_name = table.monitoring_player_names[0]
    total_win_cnt = {player_name: 0 for player_name in table.player_names}
    table.set_player_mode(PlayerMode.TRAIN)

    print_table_head()

    for train_episode in range(1, TRAINING_EPISODES_AMOUNT + 1):
        table.run_tournament()
        table.reset()
        if train_episode % validation_frequency == 0:
            table.set_player_mode(PlayerMode.VALID)
            table.activate_player_monitor()
            valid_win_cnt = {player_name: 0 for player_name in table.player_names}

            for valid_episode in range(VALIDATION_EPISODES_AMOUNT):
                table.run_tournament()
                total_win_cnt[table.get_winner()] += 1
                valid_win_cnt[table.get_winner()] += 1
                table.reset()

                score = ''
                names = ''
                for name in valid_win_cnt:
                    names += f'{name}:'
                    score += f'{valid_win_cnt.get(name)}:'

                perc = round((100 / VALIDATION_EPISODES_AMOUNT) * valid_episode, 2)
                print(
                    f'\rVALIDATING: {valid_episode}/{VALIDATION_EPISODES_AMOUNT} ({int(perc)}%)  '
                    f'{names[:-1]} - {score[:-1]}', end='')
            table.set_player_mode(PlayerMode.TRAIN)
            table.deactivate_player_monitor()
            print_table_row(train_episode, valid_win_cnt.get(monitored_player_name))
        perc = round((100 / TRAINING_EPISODES_AMOUNT) * train_episode, 2)
        print(f'\rTRAINING: {train_episode}/{TRAINING_EPISODES_AMOUNT} ({int(perc)}%)', end='')

    if SHOULD_SAVE_MODEL:
        table.save_player_model()

    table.finish()

    print()


def prepare_dqn() -> None:
    global LOAD_MODEL_PATH, ALPHA, GAMMA, EPSILON, EPSILON_FLOOR, SHOULD_EPSILON_DECAY

    NeuralNetwork.LOAD_MODEL = LOAD_MODEL_PATH
    NeuralNetwork.ALPHA = ALPHA
    NeuralNetwork.GAMMA = GAMMA

    SimpleDqnBot.EPSILON = EPSILON
    SimpleDqnBot.EPSILON_FLOOR = EPSILON_FLOOR
    SimpleDqnBot.EPSILON_DECAY = calculate_epsilon_decay()
    SimpleDqnBot.SHOULD_EPSILON_DECAY = SHOULD_EPSILON_DECAY


def prepare_monitored_dqn() -> None:
    global VALIDATION_AMOUNT

    MonitoredSimpleDqnBot.MONITOR_FREQUENCY = VALIDATION_AMOUNT


def calculate_epsilon_decay() -> float:
    global EPSILON, TRAINING_EPISODES_AMOUNT
    decay = 0

    if TRAINING_EPISODES_AMOUNT > 0:
        decay = EPSILON / TRAINING_EPISODES_AMOUNT

    return decay


def print_table_head() -> None:
    print('+------------------+-------------------------+')
    print('| Episodes trained | Validation episodes won |')
    print('+------------------+-------------------------+')


def print_table_row(episodes_trained: int, valid_episodes_won: int) -> None:
    global VALIDATION_EPISODES_AMOUNT
    won = f'{str(valid_episodes_won)}/{str(VALIDATION_EPISODES_AMOUNT)}'
    space = ' ' * 100
    print(f'\r| {str(episodes_trained):17}| {won:24}|{space}')
    print('+------------------+-------------------------+')


def main():
    play()


if __name__ == '__main__':
    main()
