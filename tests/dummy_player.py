from game import Dummy
from typing import List, Type


def create_dummy_classes(amount: int) -> List[Type[Dummy]]:
    return [Dummy for _ in range(amount)]
