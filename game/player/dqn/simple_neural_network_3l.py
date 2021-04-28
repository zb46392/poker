from . import SimpleNeuralNetwork
from torch import nn


class SimpleNeuralNetwork3L(SimpleNeuralNetwork):
    def _create_neural_network(self) -> nn.Sequential:
        in_size = self._state_interpreter.state_space
        out_size = self._state_interpreter.action_space

        network = nn.Sequential()
        network.add_module('linear_0', nn.Linear(in_features=in_size, out_features=1000))
        network.add_module('relu_0', nn.ReLU())
        network.add_module('linear_1', nn.Linear(in_features=1000, out_features=1000))
        network.add_module('relu_1', nn.ReLU())
        network.add_module('linear_2', nn.Linear(in_features=1000, out_features=1000))
        network.add_module('relu_2', nn.ReLU())
        network.add_module('linear_3', nn.Linear(in_features=1000, out_features=out_size))
        network.to(self._device)
        return network
