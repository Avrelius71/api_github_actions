from enum import StrEnum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень репозитория: чтобы .env находился при запуске pytest из подкаталогов или из IDE
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Environment(StrEnum):
    DEV = "dev"
    STAGE = "stage"


class EnvironmentConfig(BaseSettings):
    booker_url: str
    # Демо Restful Booker; переопределяются через .env или переменные окружения
    booker_username: str = "admin"
    booker_password: str = "password123"

    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


_URLS = {
    Environment.DEV: "https://restful-booker.herokuapp.com",
    Environment.STAGE: "https://restful-booker.herokuapp.com",  # Нужно заменить при наличии stage стенда
}


def load_environment(env: Environment) -> EnvironmentConfig:
    if env not in _URLS:
        raise ValueError(f"Unsupported environment: {env}")
    return EnvironmentConfig(booker_url=_URLS[env])
