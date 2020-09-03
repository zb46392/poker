from . import ReplayMemory, StateInterpreter
from .. import SemiRandomBot
from ... import Moves, State
from datetime import datetime
from random import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from typing import List, Tuple


class SimpleDqnBot(SemiRandomBot):
    States = Tuple[torch.Tensor, ...]
    PreviousStates = States
    PreviousActions = Tuple[Moves, ...]
    PreviousPossibleActions = List[Tuple[Moves, ...]]
    NextStates = States

    Batch = Tuple[PreviousStates, PreviousActions, PreviousPossibleActions, NextStates]

    ALPHA = 0.001
    GAMMA = 0.999
    EPSILON = 0.0
    EPSILON_FLOOR = 0.1
    TRAIN_EPISODES = 100_000
    SHOULD_EPSILON_DECAY = False
    SHOULD_TRACK_PROGRESS = False
    SHOULD_SAVE_MODEL_AFTER_TRAINING = False
    LOAD_MODEL = None

    def __init__(self, chips: int) -> None:
        super().__init__(chips)
        self._previous_chips = chips

        self._train_amount = SimpleDqnBot.TRAIN_EPISODES
        self._is_training = self._train_amount > 0

        self._alpha = SimpleDqnBot.ALPHA  # Learning rate
        self._gamma = SimpleDqnBot.GAMMA  # Future reward discount
        self._epsilon = SimpleDqnBot.EPSILON  # Exploration rate
        self._epsilon_floor = SimpleDqnBot.EPSILON_FLOOR
        self._should_epsilon_decay = SimpleDqnBot.SHOULD_EPSILON_DECAY
        self._epsilon_decay = self._epsilon / self._train_amount if self._train_amount > 0 else 0

        self._all_moves = [move for move in Moves]
        self._actions_indices = {self._all_moves[i]: i for i in range(len(self._all_moves))}
        self._previous_possible_moves = None
        self._previous_state = None
        self._previous_move = None
        self._current_state = None
        self._current_move = None

        self._rewards_sum = 0
        self._episode_cnt = 0
        self._replay_memory = ReplayMemory()
        self._state_interpreter = StateInterpreter(chips)

        self._device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._policy_net = self._create_neural_network()
        self._loss = nn.MSELoss()
        self._optim = optim.Adam(self._policy_net.parameters(), self._alpha)

        self._should_track_training_progress = SimpleDqnBot.SHOULD_TRACK_PROGRESS
        self._summary_writer = None

        if SimpleDqnBot.LOAD_MODEL is not None:
            self.load_model(SimpleDqnBot.LOAD_MODEL)

        self._should_save_model_after_training = SimpleDqnBot.SHOULD_SAVE_MODEL_AFTER_TRAINING

    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        self._update_states(game_state)
        self._determine_current_move(possible_moves)
        if self._is_training:
            self._execute_replay_memory_responsibilities()

        return self._current_move

    def receive_chips(self, amount: int) -> None:
        super().receive_chips(amount)
        if self._is_training:
            self._execute_training_responsibilities()

    def _create_neural_network(self) -> nn.Sequential:
        in_size = self._state_interpreter.state_space
        out_size = self._state_interpreter.action_space

        network = nn.Sequential()
        network.add_module('linear_0', nn.Linear(in_features=in_size, out_features=1000))
        network.add_module('relu_0', nn.ReLU())
        network.add_module('linear_1', nn.Linear(in_features=1000, out_features=1000))
        network.add_module('relu_1', nn.ReLU())
        network.add_module('linear_2', nn.Linear(in_features=1000, out_features=out_size))
        network.to(self._device)
        return network

    def _update_states(self, state: State) -> None:
        self._previous_state = self._current_state
        current_state = self._state_interpreter.interpret(self._hand, state, self._chips)
        self._current_state = torch.as_tensor([current_state], dtype=torch.float32).to(self._device)

    def _update_moves(self, move: Moves) -> None:
        self._previous_move = self._current_move
        self._current_move = move

    def _update_reward_sum(self, reward: int) -> None:
        self._rewards_sum += reward

    def _update_episode_cnt(self) -> None:
        self._episode_cnt += 1

    def _update_epsilon(self) -> None:
        if self._should_epsilon_decay and self._epsilon > self._epsilon_floor:
            self._epsilon -= self._epsilon_decay

    def _is_game_over(self) -> bool:
        return self._chips == 0 or self._chips == self._state_interpreter.total_chips_amount

    def _determine_current_move(self, possible_moves: List[Moves]):
        self._previous_possible_moves = possible_moves
        if random() < self._epsilon:
            self._explore(possible_moves)
        else:
            self._exploit(possible_moves)

    def _execute_replay_memory_responsibilities(self) -> None:
        if self._previous_state is not None:
            experience = (
                self._previous_state, self._previous_move,
                self._previous_possible_moves, self._current_state
            )
            self._replay_memory.insert(experience)

    def _execute_training_responsibilities(self) -> None:
        if self._previous_state is not None:
            reward = self._chips - self._previous_chips
            self._update_reward_sum(reward)
            self._update_policy_net(reward)

            if self._should_track_training_progress:
                self._track_progress()

        self._prepare_for_next_episode()

        if self._is_game_over():
            self._update_epsilon()
            self._update_episode_cnt()

            if self._episode_cnt == self._train_amount:
                self._is_training = False

                if self._should_save_model_after_training:
                    self.save_model()

    def _explore(self, possible_moves: List[Moves]) -> None:
        move = super().make_move(possible_moves, None)
        self._update_moves(move)

    def _exploit(self, possible_moves: List[Moves]) -> None:
        self._update_moves(self._choose_best_action(possible_moves))

    def _choose_best_action(self, possible_moves: List[Moves]) -> Moves:
        pred = self._inference(self._current_state)

        moves_indices_sorted = [i.item() for i in pred.sort(descending=True).indices.squeeze()]

        for i in moves_indices_sorted:
            if self._all_moves[i] in possible_moves:
                return self._all_moves[i]

    def _update_policy_net(self, reward: int) -> None:
        self._policy_net.train()

        batch = self._create_batch()
        previous_states, previous_moves, previous_possible_actions, next_states = batch

        actual_pred = self._policy_net(torch.cat(previous_states))
        target_pred = self._generate_target_preds(batch, actual_pred, reward)

        loss = self._loss(actual_pred, target_pred)
        self._optim.zero_grad()
        loss.backward()
        self._optim.step()

    def _create_batch(self) -> Batch:
        experiences = self._replay_memory.flush()
        return tuple(zip(*experiences))

    def _generate_target_preds(self, batch: Batch, preds: torch.Tensor, reward: int) -> torch.Tensor:
        previous_states, previous_moves, previous_possible_actions, next_states = batch
        discounted_reward_sums = self._calculate_discounted_reward_sums(reward, len(previous_moves))

        next_preds = self._policy_net(torch.cat(next_states))
        next_qs = next_preds.max(dim=1).values.detach()

        target_preds = torch.zeros(preds.shape).to(self._device)

        for i, ppa in enumerate(previous_possible_actions):
            indices = [self._actions_indices[a] for a in ppa]
            previous_action_i = self._actions_indices.get(previous_moves[i])
            target_preds[i][indices] = preds[i][indices]
            if ppa == previous_possible_actions[-1]:
                target_preds[i][previous_action_i] = discounted_reward_sums[i]
            else:
                target_preds[i][previous_action_i] = (next_qs[i] * self._gamma) + discounted_reward_sums[i]

        return target_preds

    def _inference(self, state: torch.Tensor) -> torch.Tensor:
        self._policy_net.eval()
        with torch.no_grad():
            pred = self._policy_net(state)

        return pred

    def save_model(self) -> None:
        now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f'{type(self).__name__}_model_{now}.weights'

        torch.save(self._policy_net.state_dict(), file_name)

    def load_model(self, file_path: str) -> None:
        state_dict = torch.load(file_path, map_location=self._device)
        self._policy_net.load_state_dict(state_dict)

    def _calculate_discounted_reward_sums(self, reward: int, steps: int) -> List[float]:
        discounted_reward_sums = []
        rewards = [0.0 for _ in range(steps)]
        rewards[-1] = float(reward)

        for i in range(steps - 1, -1, -1):
            sum_reward = self._calculate_discounted_reward_sum(rewards[i:])
            discounted_reward_sums.insert(0, sum_reward)

        return discounted_reward_sums

    def _calculate_discounted_reward_sum(self, rewards: List[float]) -> float:
        discounted_reward_sum = 0
        for i, reward in enumerate(rewards):
            discounted_reward_sum += self._gamma ** i * reward
        return discounted_reward_sum

    def _prepare_for_next_episode(self) -> None:
        self._previous_possible_moves = None
        self._previous_state = None
        self._previous_move = None
        self._current_state = None
        self._current_move = None
        self._previous_chips = self.get_amount_of_chips()

    def _track_progress(self) -> None:
        if self._summary_writer is None:
            self._init_summary_writer()

        self._write_train_summary()

    def _init_summary_writer(self) -> None:
        train_amount = self._train_amount
        self._summary_writer = SummaryWriter(
            comment=f' - {type(self).__name__} : ' +
                    f'alpha={self._alpha}, gamma={self._gamma}, '
                    f'train={train_amount}'
        )
        self._summary_writer.add_graph(self._policy_net, self._current_state)

    def _write_train_summary(self) -> None:
        if self._episode_cnt % int(self._train_amount / 100) == 0:
            self._summary_writer.add_scalar('Reward', self._rewards_sum, self._episode_cnt)

            for name, param in self._policy_net.named_parameters():
                self._summary_writer.add_histogram(name, param, self._episode_cnt)
                self._summary_writer.add_histogram(f'{name}_grad', param.grad, self._episode_cnt)
