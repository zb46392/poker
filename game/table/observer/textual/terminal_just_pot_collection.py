from .base import Base
import os


class TerminalJustPotCollection(Base):
    def _apply_new_info(self) -> None:
        if self._is_pot_collection:
            print()
            print(self._info)
            print('\nPress enter to continue...')
            input()
            os.system('cls' if os.name == 'nt' else 'clear')
