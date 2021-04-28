#!/usr/bin/env python3

from game import Table, SemiRandomBot, SimpleDqnBot, OpponentBotGold
from game.player import Mode as PlayerMode
from game.player.dqn import SimpleNeuralNetwork

VALIDATION_EPISODES = 10_000
LOAD_MODEL_PATH = 'models/model_random_alpha_0_01__6724.pt'
# LOAD_MODEL_PATH = 'models/model_opponent_alpha_0_1.pt'
# LOAD_MODEL_PATH = 'models/model_3000_alpha_0_1__6010.pt'
INIT_CHIPS = 10
PLAYERS = [SimpleDqnBot, SemiRandomBot, SemiRandomBot]


def main() -> None:
    global VALIDATION_EPISODES, INIT_CHIPS

    Table.INIT_CHIPS = INIT_CHIPS
    prepare_dqn()

    table = Table(PLAYERS)

    total_win_cnt = {player_name: 0 for player_name in table.player_names}

    for episode in range(1, VALIDATION_EPISODES + 1):
        table.reset_tournament()
        table.run_tournament()

        total_win_cnt[table.get_winner_name()] += 1

        print_progress(episode, total_win_cnt)

    print_results(total_win_cnt)


def prepare_dqn() -> None:
    global LOAD_MODEL_PATH

    SimpleNeuralNetwork.LOAD_MODEL = LOAD_MODEL_PATH
    SimpleDqnBot.MODE = PlayerMode.VALID


def print_progress(episode: int, total_win_cnt: dict) -> None:
    global VALIDATION_EPISODES

    names = ''.join([f'{name}:' for name in total_win_cnt])
    score = ''.join([f'{total_win_cnt.get(name)}:' for name in total_win_cnt])

    perc = round((100 / VALIDATION_EPISODES) * episode, 2)
    print(
        f'\rVALIDATING: {episode}/{VALIDATION_EPISODES} ({int(perc)}%)  '
        f'{names[:-1]} - {score[:-1]}', end='')


def print_results(total_win_cnt: dict) -> None:
    print()
    for name in total_win_cnt:
        print(f'{name}: {total_win_cnt.get(name)}')


if __name__ == '__main__':
    main()
