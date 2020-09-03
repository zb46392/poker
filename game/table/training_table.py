from . import Table
from typing import List


class TrainingTable(Table):
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
