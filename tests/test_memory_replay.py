from game.player.dqn import ReplayMemory
import unittest
from unittest import TestCase


class TestReplayMemory(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._mem_replay = ReplayMemory()

    def test_initialization(self) -> None:
        mem_size = 64000
        batch_size = 128

        mem_replay = ReplayMemory(memory_size=mem_size, batch_size=batch_size)

        self.assertEqual(mem_size, mem_replay.memory_size)
        self.assertEqual(batch_size, mem_replay.batch_size)

    def test_insertion(self) -> None:
        experience = ((1, 2, 4), ('a', 'b', 'r'), (71, '000', True))
        self._mem_replay.insert(experience)

        memory = self._mem_replay._memory[0]

        self.assertEqual(experience, memory)

    def test_insertion_at_beginning_on_overflow(self):
        reply_mem = ReplayMemory(memory_size=2, batch_size=1)

        first = (('testing', 'replay memory'), ('insertion', 'on overflow'))
        second = ((111, 222, 333), (True, False, True), ([44, 55], [66, 77, 88]))
        third = ('x', 'y', 'z')

        reply_mem.insert(first)
        reply_mem.insert(second)
        reply_mem.insert(third)
        reply_mem.insert(first)

        memory_one = reply_mem._memory[0]
        memory_two = reply_mem._memory[1]

        self.assertEqual(third, memory_one)
        self.assertEqual(first, memory_two)

        reply_mem.insert(second)
        memory_three = reply_mem._memory[0]

        self.assertEqual(second, memory_three)

    def test_batch_size_greater_than_memory_size(self) -> None:
        memory_size = 32
        batch_size = 64

        self.assertRaises(Exception, ReplayMemory, memory_size=memory_size, batch_size=batch_size)

    def test_can_sample(self) -> None:
        replay_mem = ReplayMemory(memory_size=8, batch_size=2)

        memory_one = (1, 2, 3)
        memory_two = ('a', 'b', 'c')

        replay_mem.insert(memory_one)
        self.assertFalse(replay_mem.can_sample())

        replay_mem.insert(memory_two)
        self.assertTrue(replay_mem.can_sample())

    def test_sample(self) -> None:
        memory_size = 8
        batch_size = 2
        replay_mem = ReplayMemory(memory_size, batch_size)
        memories = [i for i in range(10)]

        replay_mem.insert(memories[0])
        self.assertRaises(Exception, replay_mem.get_sample)

        replay_mem.insert(memories[1])

        batch = replay_mem.get_sample()
        self.assertEqual(batch_size, len(batch))

        for i in range(2, 10):
            replay_mem.insert(memories[i])

        batch = replay_mem.get_sample()
        self.assertEqual(batch_size, len(batch))

    def test_flush_memory(self) -> None:
        first = 1
        second = 'x'
        third = {'1x': 10}

        self._mem_replay.insert(first)
        self._mem_replay.insert(second)
        self._mem_replay.insert(third)

        flushed = self._mem_replay.flush()

        self.assertEqual([first, second, third], flushed)
        self.assertTrue(len(self._mem_replay._memory) == 0)


if __name__ == '__main__':
    unittest.main()
