from pathlib import Path
from datetime import datetime


class Utils:
    BASE_DIR = Path(__file__).parent.parent.parent

    @classmethod
    def get_base_dir(cls) -> Path:
        return cls.BASE_DIR

    @staticmethod
    def create_directory(path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_now_as_str() -> str:
        return datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
