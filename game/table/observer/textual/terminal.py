from .base import Base


class Terminal(Base):
    def _apply_new_info(self) -> None:
        print(self._info)
