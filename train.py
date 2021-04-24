#!/usr/bin/env python3

from game import SemiRandomBot, SimpleDqnBot, OpponentBotGold, OpponentBotSilver
from game import Table, TrainingTable
from game.table.observer import TerminalObserver, FileObserver
from game.player import Mode as PlayerMode
from game.player.dqn import NeuralNetwork
from game.player.monitor import MonitoredSimpleDqnBot
from typing import Dict

ALPHA = 0.1
GAMMA = 0.999
EPSILON = 1.0
EPSILON_FLOOR = 0.1
SHOULD_EPSILON_DECAY = True

TRAINING_EPISODES_AMOUNT = 100
VALIDATION_EPISODES_AMOUNT = 5
VALIDATION_AMOUNT = 100
MONITOR_AMOUNT = VALIDATION_AMOUNT

SHOULD_MONITOR_TRAINING = False
SHOULD_MONITOR_VALIDATION = True

# LOAD_MODEL_PATH = 'models/SimpleDqnBot_model_2020_09_20_19_27_49.weights'
LOAD_MODEL_PATH = None
SHOULD_SAVE_MODEL = True
INIT_CHIPS = 10
PLAYERS = [MonitoredSimpleDqnBot, SemiRandomBot, SemiRandomBot]


def play():
    global TRAINING_EPISODES_AMOUNT, VALIDATION_EPISODES_AMOUNT, SHOULD_SAVE_MODEL

    validation_frequency = calculate_validation_frequency()

    prepare_dqn()
    prepare_monitored_dqn()
    table = initiate_table()
    total_win_cnt = {player_name: 0 for player_name in table.player_names}
    prepare_training_monitor(table)

    print_table_head()
    progress_msg = ''

    for train_episode in range(1, TRAINING_EPISODES_AMOUNT + 1):
        table.reset_tournament()
        table.run_tournament()

        if train_episode % validation_frequency == 0:
            table.set_player_mode(PlayerMode.VALID)
            table.activate_player_monitor()
            valid_win_cnt = {player_name: 0 for player_name in total_win_cnt}

            prepare_validation_monitor(table)

            for valid_episode in range(VALIDATION_EPISODES_AMOUNT):
                table.reset_tournament()
                table.run_tournament()

                total_win_cnt[table.get_winner_name()] += 1
                valid_win_cnt[table.get_winner_name()] += 1

                progress_msg = generate_valid_progress_msg(valid_episode, valid_win_cnt)
                print(f'\r{progress_msg}', end='')
            table.set_player_mode(PlayerMode.TRAIN)

            print_table_row(train_episode, table, valid_win_cnt, progress_msg)

            prepare_training_monitor(table)

        progress_msg = generate_train_progress_msg(train_episode)
        print(f'\r{progress_msg}', end='')

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
    global MONITOR_AMOUNT, TRAINING_EPISODES_AMOUNT, VALIDATION_EPISODES_AMOUNT
    global SHOULD_MONITOR_TRAINING, SHOULD_MONITOR_VALIDATION

    monitor_frequency = TRAINING_EPISODES_AMOUNT + VALIDATION_EPISODES_AMOUNT + 1
    total_monitoring_episodes = 0

    if SHOULD_MONITOR_TRAINING:
        total_monitoring_episodes += TRAINING_EPISODES_AMOUNT

    if SHOULD_MONITOR_VALIDATION:
        total_monitoring_episodes += VALIDATION_EPISODES_AMOUNT

    if MONITOR_AMOUNT > 0 and total_monitoring_episodes > 0:
        monitor_frequency = int(total_monitoring_episodes / MONITOR_AMOUNT)

        if monitor_frequency < 1:
            monitor_frequency = 1

    MonitoredSimpleDqnBot.MONITOR_FREQUENCY = monitor_frequency


def calculate_epsilon_decay() -> float:
    global EPSILON, TRAINING_EPISODES_AMOUNT
    decay = 0

    if TRAINING_EPISODES_AMOUNT > 0:
        decay = EPSILON / TRAINING_EPISODES_AMOUNT

    return decay


def initiate_table() -> TrainingTable:
    global INIT_CHIPS, PLAYERS

    Table.INIT_CHIPS = INIT_CHIPS
    table = TrainingTable(PLAYERS)
    table.set_player_mode(PlayerMode.TRAIN)

    return table


def calculate_validation_frequency() -> int:
    global TRAINING_EPISODES_AMOUNT, VALIDATION_AMOUNT

    validation_frequency = TRAINING_EPISODES_AMOUNT + 1
    if VALIDATION_AMOUNT > 0:
        validation_frequency = TRAINING_EPISODES_AMOUNT / VALIDATION_AMOUNT

    return int(validation_frequency)


def prepare_training_monitor(table: TrainingTable) -> None:
    global SHOULD_MONITOR_TRAINING

    prepare_monitoring(table, SHOULD_MONITOR_TRAINING)


def prepare_validation_monitor(table: TrainingTable) -> None:
    global SHOULD_MONITOR_VALIDATION

    prepare_monitoring(table, SHOULD_MONITOR_VALIDATION)


def prepare_monitoring(table: TrainingTable, should_monitor: bool) -> None:
    if should_monitor:
        table.activate_player_monitor()
    else:
        table.deactivate_player_monitor()


def generate_valid_progress_msg(valid_episode: int, valid_win_cnt: Dict[str, int]) -> str:
    global VALIDATION_EPISODES_AMOUNT

    score = ''
    names = ''
    for name in valid_win_cnt:
        names += f'{name}:'
        score += f'{valid_win_cnt.get(name)}:'

    perc = round((100 / VALIDATION_EPISODES_AMOUNT) * valid_episode, 2)

    return f'VALIDATING: {valid_episode}/{VALIDATION_EPISODES_AMOUNT} ({int(perc)}%)  {names[:-1]} - {score[:-1]}'


def generate_train_progress_msg(train_episode: int) -> str:
    global TRAINING_EPISODES_AMOUNT

    perc = round((100 / TRAINING_EPISODES_AMOUNT) * train_episode, 2)
    return f'TRAINING: {train_episode}/{TRAINING_EPISODES_AMOUNT} ({int(perc)}%)'


def print_table_head() -> None:
    print('+------------------+-----------------------------------+-------------------------+')
    print('| Episodes trained |            Player name            | Validation episodes won |')
    print('+------------------+-----------------------------------+-------------------------+')


def print_table_row(episodes_trained: int, table: TrainingTable,
                    valid_win_cnt: Dict[str, int], previous_msg: str) -> None:
    global VALIDATION_EPISODES_AMOUNT
    training_player_names = table.trainable_player_names

    row = ''
    for i, monitoring_player_name in enumerate(training_player_names):
        episodes_won = valid_win_cnt.get(monitoring_player_name)
        won = f'{str(episodes_won)}/{str(VALIDATION_EPISODES_AMOUNT)}'
        row += f'|{str(episodes_trained) if i == 0 else str():18}| {monitoring_player_name:34}| {won:24}|'

        space_amount = (len(previous_msg) - len(row)) if len(previous_msg) > len(row) else 0
        space = ' ' * space_amount

        row += f'{space}\n'

    print(f'\r{row[:-1]}')
    print('+------------------+-----------------------------------+-------------------------+')


def main():
    play()


if __name__ == '__main__':
    main()
