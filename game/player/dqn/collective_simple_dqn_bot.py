from . import SimpleDqnBot, SimpleNeuralNetworkSingleton, SimpleNeuralNetwork


class CollectiveSimpleDqnBot(SimpleDqnBot):
    def _obtain_neural_network(self) -> SimpleNeuralNetwork:
        return SimpleNeuralNetworkSingleton.get_instance()
