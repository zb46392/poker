from . import Monitor
from .. import SimpleDqnBot, Mode

from typing import Dict


class MonitoredSimpleDqnBot(SimpleDqnBot):
    def __init__(self, chips: int) -> None:
        super().__init__(chips)
        self._average_win = 0
        self._calculation_cnt = 0
        self._monitor = Monitor(self._policy_net, self._generate_monitoring_comment_params())
        self._is_monitoring = False

    def activate_monitoring(self) -> None:
        self._reset_average_calculation()
        self._is_monitoring = True

    def deactivate_monitoring(self) -> None:
        self._monitor.update_progress(self._average_win)
        self._monitor.monitor()
        self._is_monitoring = False

    def _generate_monitoring_comment_params(self) -> Dict[str, str]:
        return {
            'alpha': self._alpha,
            'gamma': self._gamma,
            'epsilon': self._epsilon,
            'epsilon_floor': self._epsilon_floor,
            'epsilon_decay': self._epsilon_decay
        }

    def _calculate_running_average_win(self) -> None:
        self._calculation_cnt += 1
        self._average_win = self._average_win + (self._reward - self._average_win) / self._calculation_cnt

    def receive_chips(self, amount: int) -> None:
        super().receive_chips(amount)
        if self._is_monitoring:
            self._calculate_running_average_win()

    def _reset_average_calculation(self) -> None:
        self._average_win = 0
        self._calculation_cnt = 0

    def close(self) -> None:
        self._monitor.close()
