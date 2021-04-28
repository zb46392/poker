from . import SimpleNeuralNetwork


class SimpleNeuralNetworkSingleton:
    INSTANCE = None

    def __init__(self) -> None:
        raise RuntimeError('Call get_instance() instead')

    @classmethod
    def get_instance(cls) -> SimpleNeuralNetwork:
        if cls.INSTANCE is None:
            cls.INSTANCE = SimpleNeuralNetwork()

        return cls.INSTANCE
