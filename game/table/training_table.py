from game.table import Table
from game.player import Player as BasePlayer, Mode, SimpleDqnBot, MonitoredSimpleDqnBot, CollectiveSimpleDqnBot
from typing import List, Type


class TrainingTable(Table):
    def __init__(self, players_classes: List[Type[BasePlayer]]) -> None:
        super().__init__(players_classes)
        self._monitorable_player_class_names = [MonitoredSimpleDqnBot.__name__]
        self._trainable_player_class_names = [SimpleDqnBot.__name__, MonitoredSimpleDqnBot.__name__,
                                              CollectiveSimpleDqnBot.__name__]
        self._monitoring_players = []
        self._training_players = []

        self._acquire_special_players()

    def _acquire_special_players(self) -> None:
        for player in self._players:
            if player.player_type in self._monitorable_player_class_names:
                self._monitoring_players.append(player.basic_player)

            if player.player_type in self._trainable_player_class_names:
                self._training_players.append(player.basic_player)

    @property
    def players(self) -> List[BasePlayer]:
        return [p.basic_player for p in self._players]

    @property
    def trainable_player_names(self) -> List[str]:
        names = [player.name for player in self._training_players]
        return names

    def activate_player_monitor(self) -> None:
        for player in self._monitoring_players:
            player.activate_monitoring()

    def deactivate_player_monitor(self) -> None:
        for player in self._monitoring_players:
            player.deactivate_monitoring()
            player.reset_progress()

    def set_player_mode(self, mode: Mode) -> None:
        for player in self._training_players:
            player.mode = mode

    def save_player_model(self) -> None:
        for player in self._training_players:
            player.save_model()

    def finish(self) -> None:
        for player in self._monitoring_players:
            player.close()
