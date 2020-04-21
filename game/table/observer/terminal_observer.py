from . import TextualObserver


class TerminalObserver(TextualObserver):
    def _apply_new_msg(self, msg: str) -> None:
        print(msg)
