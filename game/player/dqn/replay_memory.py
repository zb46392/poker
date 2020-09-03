from random import sample
from typing import Any, List


class ReplayMemory:
    def __init__(self, memory_size: int = 512, batch_size: int = 64) -> None:
        if batch_size > memory_size:
            raise Exception('Batch size cannot exceed memory size')

        self._memory_size = memory_size
        self._batch_size = batch_size
        self._memory = []
        self._memory_index = 0

    @property
    def memory_size(self) -> int:
        return self._memory_size

    @property
    def batch_size(self) -> int:
        return self._batch_size

    def can_sample(self) -> bool:
        return len(self._memory) >= self._batch_size

    def get_sample(self) -> List[Any]:
        return sample(self._memory, self._batch_size)

    def insert(self, experience: Any) -> None:
        if len(self._memory) < self._memory_size:
            self._memory.append(experience)
        else:
            self._memory[self._memory_index] = experience
            self._update_memory_index()

    def flush(self) -> List[Any]:
        memory = self._memory
        self._memory = []
        return memory

    def _update_memory_index(self) -> None:
        self._memory_index += 1

        if self._memory_index >= self._memory_size:
            self._memory_index = 0
