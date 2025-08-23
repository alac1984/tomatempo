import logging
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Annotated, Literal

from platformdirs import PlatformDirs
from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["dev", "staging", "prod", "test"]
LogName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

_LOG_MAP: dict[LogName, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class Settings(BaseSettings):
    """
    Centralizes all application settings.

    - Loads values from:
    1. Explicit arguments in the constructor (Settings(environment="prod"));
    2. Environment variables with the APP_ prefix (e.g., APP_ENVIRONMENT=prod);
    3. The .env file, if present;
    4. Default values defined in the class.

    - Includes normalization and validation of environment and log_level;
    - Exposes computed properties (is_prod, debug, log_level_numeric);
    - Manages configuration, cache, and log directories using platformdirs;
    - Can be used as a singleton via get_settings().
    """

    # App identity / dirs
    app_name: str = "tomatempo"
    app_author: str = "André Carvalho"
    roaming: bool = True
    ensure_dirs: bool = True  # create folders if they don't exist

    # Logging / environment
    environment: Environment = "dev"
    log_level: LogName = "INFO"

    # Database
    database_url: Annotated[str, Field(validate_default=True)] = "sqlite:///./data.db"

    # Config dictionary
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        case_sensitive=False,  # Windows friendly
        extra="ignore",
        env_nested_delimiter="__",
        validate_assignment=True,
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def _coerce_log_level(cls, v: str) -> LogName:
        """Validate log_level"""
        v = str(v).upper()
        if v not in _LOG_MAP:
            raise ValueError(f"invalid log_level {v}. Use {list(_LOG_MAP)}.")
        return v  # type: ignore[return-value]

    @field_validator("environment", mode="before")
    @classmethod
    def _coerce_environment(cls, v: str) -> Environment:
        """Validate environment"""
        v = str(v).lower()
        valid = ["dev", "staging", "prod", "test"]
        if v not in valid:
            raise ValueError(f"invalid environment {v}. Use {valid}.")
        return v  # type: ignore[return-value]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def log_level_numeric(self) -> int:
        """Numeric level for logging.basicConfig."""
        return _LOG_MAP[self.log_level]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_prod(self) -> bool:
        return self.environment == "prod"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def debug(self) -> bool:
        return self.environment in {"dev", "test"}

    # ------- Plataform Dirs ------

    @cached_property
    def _dirs(self) -> PlatformDirs:
        return PlatformDirs(appname=self.app_name, appauthor=self.app_author, roaming=self.roaming)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cache_dir(self) -> Path:
        p = Path(self._dirs.user_cache_dir)
        if self.ensure_dirs:
            p.mkdir(parents=True, exist_ok=True)
        return p

    @computed_field  # type: ignore[prop-decorator]
    @property
    def logs_dir(self) -> Path:
        p = Path(self._dirs.user_log_dir)
        if self.ensure_dirs:
            p.mkdir(parents=True, exist_ok=True)
        return p

    @computed_field  # type: ignore[prop-decorator]
    @property
    def config_dir(self) -> Path:
        p = Path(self._dirs.user_config_dir)
        if self.ensure_dirs:
            p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton with cache enabled"""

    return Settings()


def reload_settings() -> Settings:
    """For tests and changing env vars"""
    get_settings.cache_clear()
    return get_settings()
