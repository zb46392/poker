from . import SimpleDqnBot, SimpleNeuralNetwork3L


class SimpleDqnBot3l(SimpleDqnBot):
    @staticmethod
    def _obtain_neural_network() -> SimpleNeuralNetwork3L:
        return SimpleNeuralNetwork3L()
