import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings:
    TDML_PORT: int = int(os.getenv("TDML_PORT", "9001"))
    DB_PATH: str = os.getenv("DB_PATH", str(DATA_DIR / "simulator.db"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.DB_PATH}"


settings = Settings()
