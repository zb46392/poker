from .state_interpreter import InterpretableState
from game import Utils
from game.player.dqn.state_interpreter import StateInterpreterV2 as StateInterpreter
from game.player import Mode
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Tuple, Optional

State = torch.Tensor
PreviousState = State
PreviousAction = int
PreviousPossibleActions = Tuple[int, ...]
NextState = State
Experience = Tuple[PreviousState, PreviousAction, PreviousPossibleActions, NextState]

States = Tuple[State, ...]
PreviousStates = States
PreviousActions = Tuple[PreviousAction, ...]
AllPreviousPossibleActionsThisRound = Tuple[PreviousPossibleActions, ...]
NextStates = States
BatchOfExperiences = Tuple[PreviousStates, PreviousActions, AllPreviousPossibleActionsThisRound, NextStates]


class SimpleNeuralNetwork:
    ALPHA = 0.0001
    GAMMA = 0.999
    LOAD_PATH = None
    SAVE_DIR = 'models'

    def __init__(self):
        self._alpha = self.ALPHA  # Learning rate
        self._gamma = self.GAMMA  # Future reward discount

        self._state_interpreter = StateInterpreter()
        self._device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._policy_net = self._create_neural_network()
        self._loss = nn.MSELoss()
        self._optim = optim.Adam(self._policy_net.parameters(), self._alpha)

        if self.LOAD_PATH is not None:
            self.load(self.LOAD_PATH)

        self._save_dir_path = Utils.get_base_dir().joinpath(self.SAVE_DIR)

    @property
    def alpha(self) -> float:
        return self._alpha

    @property
    def gamma(self) -> float:
        return self._gamma

    @property
    def model(self) -> nn.Module:
        return self._policy_net

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

    def activate_mode(self, mode: Mode) -> None:
        if mode is Mode.TRAIN:
            self._policy_net.train()
        else:
            self._policy_net.eval()

    def interpret_state(self, interpretable_state: InterpretableState) -> torch.Tensor:
        interpreted_state = self._state_interpreter.interpret(interpretable_state)
        return torch.as_tensor([interpreted_state], dtype=torch.float32).to(self._device)

    def learn_from_experiences(self, experiences: BatchOfExperiences, reward: float) -> None:
        self._update_policy_net(experiences, reward)

    def make_decision(self, state: torch.Tensor) -> Tuple[int, ...]:
        pred = self._inference(state)
        decision = tuple([i.item() for i in pred.sort(descending=True).indices.squeeze()])

        return decision

    def _update_policy_net(self, batch: BatchOfExperiences, reward: float) -> None:
        previous_states, previous_actions, previous_possible_actions, next_states = batch

        actual_pred = self._policy_net(torch.cat(previous_states))
        target_pred = self._generate_target_preds(batch, actual_pred, reward)

        loss = self._loss(actual_pred, target_pred)
        self._optim.zero_grad()
        loss.backward()
        self._optim.step()

    def _generate_target_preds(self, batch: BatchOfExperiences, preds: torch.Tensor, reward: float) -> torch.Tensor:
        previous_states, previous_actions, previous_possible_actions, next_states = batch
        discounted_reward_sums = self._calculate_discounted_reward_sums(len(previous_actions), reward)

        next_preds = self._policy_net(torch.cat(next_states))
        next_qs = next_preds.max(dim=1).values.detach()

        target_preds = torch.zeros(preds.shape).to(self._device)

        for i, ppa in enumerate(previous_possible_actions):
            target_preds[i][list(ppa)] = preds[i][list(ppa)]
            if i == len(previous_possible_actions) - 1:
                target_preds[i][previous_actions[i]] = discounted_reward_sums[i]
            else:
                target_preds[i][previous_actions[i]] = (next_qs[i] * self._gamma) + discounted_reward_sums[i]

        return target_preds

    def _inference(self, state: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            pred = self._policy_net(state)

        return pred

    def save(self, name: Optional[str] = None) -> None:
        if not self._save_dir_path.exists():
            Utils.create_directory(self._save_dir_path)

        if name is None:
            name = f'{type(self).__name__}_{Utils.get_now_as_str()}'

        name += '.pt'

        torch.save(self._policy_net.state_dict(), self._save_dir_path.joinpath(name))

    def load(self, file_path: str) -> None:
        state_dict = torch.load(file_path, map_location=self._device)
        self._policy_net.load_state_dict(state_dict)

    def _calculate_discounted_reward_sums(self, steps: int, reward: float) -> List[float]:
        discounted_reward_sums = []
        rewards = [0.0 for _ in range(steps)]
        rewards[-1] = reward

        for i in range(steps - 1, -1, -1):
            sum_reward = self._calculate_discounted_reward_sum(rewards[i:])
            discounted_reward_sums.insert(0, sum_reward)

        return discounted_reward_sums

    def _calculate_discounted_reward_sum(self, rewards: List[float]) -> float:
        discounted_reward_sum = 0
        for i, reward in enumerate(rewards):
            discounted_reward_sum += self._gamma ** i * reward
        return discounted_reward_sum
