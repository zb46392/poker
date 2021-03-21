from game.table import Table
from game.player import Player as BasePlayer, Mode, SimpleDqnBot
from game.player.monitor import MonitoredSimpleDqnBot
from typing import List, Type


class TrainingTable(Table):
    def __init__(self, players_classes: List[Type[BasePlayer]]) -> None:
        super().__init__(players_classes)
        self._monitorable_player_class_names = [MonitoredSimpleDqnBot.__name__]
        self._trainable_player_class_names = [SimpleDqnBot.__name__, MonitoredSimpleDqnBot.__name__]
        self._monitoring_players = []
        self._training_players = []

        self._acquire_special_players()

    def _acquire_special_players(self) -> None:
        for player in self._players:
            if player.player_type in self._monitorable_player_class_names:
                self._monitoring_players.append(player.basic_player)

            if player.player_type in self._trainable_player_class_names:
                self._training_players.append(player.basic_player)

    def reset(self) -> None:
        self._reset_players()
        self._reset_player_chips()
        self._reset_play()
        self._is_game_active = True

    def _reset_players(self) -> None:
        players = []

        for p in self._players_who_lost:
            players.append(p)

        for p in self._players:
            players.append(p)

        np = None
        for p in players:
            if np is not None:
                np.next = p
            np = p
        np.next = players[0]
        self._players = np.next
        self._players_who_lost = []

    def _reset_player_chips(self) -> None:
        for p in self._players:
            a = p.get_amount_of_chips()
            p.spend_chips(a)
            p.receive_chips(self.INIT_CHIPS)

    def get_winner(self) -> str:
        if self._players.count() == 1:
            return self._players.name
        return str(None)

    @property
    def player_names(self) -> List[str]:
        names = []
        for player in self._players:
            names.append(player.name)

        return names

    @property
    def monitoring_player_names(self) -> List[str]:
        names = []
        for player in self._players:
            if player.basic_player in self._monitoring_players:
                names.append(player.name)

        return names

    def activate_player_monitor(self) -> None:
        for player in self._monitoring_players:
            player.activate_monitoring()

    def deactivate_player_monitor(self) -> None:
        for player in self._monitoring_players:
            player.deactivate_monitoring()

    def set_player_mode(self, mode: Mode) -> None:
        for player in self._training_players:
            player.mode = mode

    def save_player_model(self) -> None:
        for player in self._training_players:
            player.save_model()

    def finish(self) -> None:
        for player in self._monitoring_players:
            player.close()
