from . import Monitor, SimpleDqnBot

from typing import Dict, Optional


class MonitoredSimpleDqnBot(SimpleDqnBot):
    MONITOR_FREQUENCY = 100
    SHOULD_SAVE_BEST_AVERAGE = True
    BEST_MODEL_NAME = 'best_model'

    def __init__(self, chips: int, name: Optional[str]) -> None:
        super().__init__(chips, name)
        self._average_win = 0
        self._best_average = 0
        self._calculation_cnt = 0
        self._monitor_episode_cnt = 0
        self._monitor = Monitor(self._nn.model, self._generate_monitoring_comment_params())
        self._monitor_frequency = self.MONITOR_FREQUENCY
        self._is_monitoring = False
        self._best_model_name = self.BEST_MODEL_NAME
        self._should_save_best_average = self.SHOULD_SAVE_BEST_AVERAGE

    def activate_monitoring(self) -> None:
        self._is_monitoring = True

    def deactivate_monitoring(self) -> None:
        self._is_monitoring = False

    def reset_progress(self) -> None:
        self._reset_average_calculation()

    def _generate_monitoring_comment_params(self) -> Dict[str, str]:
        return {
            'alpha': self._nn.alpha,
            'gamma': self._nn.gamma,
            'epsilon': self._epsilon,
            'epsilon_floor': self._epsilon_floor,
            'epsilon_decay': self._epsilon_decay
        }

    def _calculate_running_average_win(self) -> None:
        self._calculation_cnt += 1
        self._average_win = self._average_win + (self._current_reward - self._average_win) / self._calculation_cnt

    def receive_chips(self, amount: int) -> None:
        super().receive_chips(amount)
        if self._is_monitoring:
            self._calculate_running_average_win()

            if self._is_game_over():
                self._monitor_episode_cnt += 1

                if self._monitor_episode_cnt % self._monitor_frequency == 0:
                    self._monitor.update_progress(self._average_win)
                    self._monitor.monitor()

                    if self._should_save_best_average and self._average_win > self._best_average:
                        self.save_model(self._best_model_name)
                        self._best_average = self._average_win

    def _reset_average_calculation(self) -> None:
        self._average_win = 0
        self._calculation_cnt = 0

    def close(self) -> None:
        self._monitor.close()
