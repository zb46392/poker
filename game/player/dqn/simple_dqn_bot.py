from . import ReplayMemory
from .neural_network import NeuralNetwork, Experience, BatchOfExperiences
from .state_interpreter import InterpretableState
from .. import SemiRandomBot, Mode
from ... import Moves, State
from random import random
from typing import List


class SimpleDqnBot(SemiRandomBot):
    EPSILON = 1.0
    EPSILON_FLOOR = 0.1
    EPSILON_DECAY = 1e-06
    MODE = Mode.TRAIN
    SHOULD_EPSILON_DECAY = False

    def __init__(self, chips: int) -> None:
        super().__init__(chips)
        self._starting_chips_amount = self.get_amount_of_chips()
        self._total_chips_amount = None
        self._all_moves = [move for move in Moves]
        self._moves_indices = {self._all_moves[i]: i for i in range(len(self._all_moves))}

        self._mode = SimpleDqnBot.MODE

        self._epsilon = SimpleDqnBot.EPSILON  # Exploration rate
        self._epsilon_floor = SimpleDqnBot.EPSILON_FLOOR
        self._should_epsilon_decay = SimpleDqnBot.SHOULD_EPSILON_DECAY
        self._epsilon_decay = SimpleDqnBot.EPSILON_DECAY

        self._previous_possible_moves = None
        self._previous_state = None
        self._previous_move = None
        self._previous_chips = None
        self._current_possible_moves = None
        self._current_state = None
        self._current_move = None
        self._current_chips = None
        self._current_reward = 0

        self._replay_memory = ReplayMemory()
        self._nn = NeuralNetwork.get_instance()

    @property
    def mode(self) -> Mode:
        return self._mode

    @mode.setter
    def mode(self, mode: Mode) -> None:
        self._mode = mode
        self._nn.activate_mode(mode)

    def make_move(self, possible_moves: List[Moves], state: State) -> Moves:
        self._update_states(state)
        self._update_chips()
        self._determine_current_move(possible_moves)
        if self._mode is Mode.TRAIN:
            self._execute_replay_memory_responsibilities()

        if self._total_chips_amount is None:
            self._determine_total_chips_amount(state)

        return self._current_move

    def receive_chips(self, amount: int) -> None:
        super().receive_chips(amount)
        self._update_current_reward()
        if self._mode is Mode.TRAIN:
            self._execute_training_responsibilities()

        self._prepare_next_round()

    def _update_states(self, state: State) -> None:
        self._previous_state = self._current_state
        self._current_state = state

    def _update_moves(self, move: Moves, possible_moves: List[Moves]) -> None:
        self._previous_possible_moves = self._current_possible_moves
        self._current_possible_moves = possible_moves
        self._previous_move = self._current_move
        self._current_move = move

    def _update_chips(self) -> None:
        self._previous_chips = self._current_chips
        self._current_chips = self.get_amount_of_chips()

    def _update_epsilon(self) -> None:
        if self._should_epsilon_decay and self._epsilon > self._epsilon_floor:
            self._epsilon -= self._epsilon_decay

    def _update_current_reward(self) -> None:
        if self._current_chips is not None and self._previous_chips is not None:
            self._current_reward = self._current_chips - self._previous_chips

    def _is_game_over(self) -> bool:
        return self._chips == 0 or self._chips == self._total_chips_amount

    def _determine_current_move(self, possible_moves: List[Moves]) -> None:
        if self._mode is Mode.TRAIN and random() < round(self._epsilon, 2):
            self._explore(possible_moves)
        else:
            self._exploit(possible_moves)

    def _determine_total_chips_amount(self, state: State) -> None:
        self._total_chips_amount = state.total_nbr_of_players * self._starting_chips_amount

    def _execute_replay_memory_responsibilities(self) -> None:
        if self._previous_state is not None:
            self._replay_memory.insert(self._create_experience())

    def _execute_training_responsibilities(self) -> None:
        if self._previous_state is not None:
            self._nn.learn_from_experiences(self._flush_batch_of_experiences(), self._current_reward)

        if self._is_game_over():
            self._update_epsilon()

    def _explore(self, possible_moves: List[Moves]) -> None:
        move = super().make_move(possible_moves, None)
        self._update_moves(move, possible_moves)

    def _exploit(self, possible_moves: List[Moves]) -> None:
        self._update_moves(self._choose_best_action(possible_moves), possible_moves)

    def _choose_best_action(self, possible_moves: List[Moves]) -> Moves:
        interpretable_state = InterpretableState(game_state=self._current_state,
                                                 hand=tuple(self.get_hand()),
                                                 current_chips_amount=self._current_chips,
                                                 initial_chips_amount=self._starting_chips_amount)
        decision = self._nn.make_decision(self._nn.interpret_state(interpretable_state))

        for i in decision:
            if self._all_moves[i] in possible_moves:
                return self._all_moves[i]

    def _create_experience(self) -> Experience:
        previous_move_index = self._moves_indices.get(self._previous_move)
        interpretable_previous_state = InterpretableState(game_state=self._previous_state,
                                                          hand=tuple(self.get_hand()),
                                                          current_chips_amount=self._previous_chips,
                                                          initial_chips_amount=self._starting_chips_amount)
        interpretable_current_state = InterpretableState(game_state=self._current_state,
                                                         hand=tuple(self.get_hand()),
                                                         current_chips_amount=self._current_chips,
                                                         initial_chips_amount=self._starting_chips_amount)
        previous_possible_moves_indices = tuple([self._moves_indices[a] for a in self._previous_possible_moves])

        return (
            self._nn.interpret_state(interpretable_previous_state), previous_move_index,
            previous_possible_moves_indices, self._nn.interpret_state(interpretable_current_state)
        )

    def _flush_batch_of_experiences(self) -> BatchOfExperiences:
        experiences = self._replay_memory.flush()
        return tuple(zip(*experiences))

    def _prepare_next_round(self) -> None:
        self._previous_possible_moves = None
        self._previous_state = None
        self._previous_move = None
        self._previous_chips = None
        self._current_possible_moves = None
        self._current_state = None
        self._current_move = None
        self._current_chips = None
