import os
from pathlib import Path

import pytest

from tomatempo.settings import Settings


@pytest.fixture
def clean_settings(tmp_path):
    def clean(m: pytest.MonkeyPatch, tmp: Path) -> None:
        # Cleaning env vars
        m.delenv("XDG_CONFIG_HOME", raising=False)
        m.delenv("XDG_STATE_HOME", raising=False)
        m.delenv("XDG_CACHE_HOME", raising=False)

        # Cleaning APP env vars
        for v in list(os.environ):
            if v.startswith("APP_"):
                m.delenv(v, raising=False)

        # Setting new cwd
        m.chdir(tmp)

        # New directories
        m.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
        m.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
        m.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

        # Remove .env file
        (tmp / ".env").unlink(missing_ok=True)

    return clean


@pytest.fixture
def tsettings(clean_settings, tmp_path, monkeypatch):
    """
    Create a default test settings instance and change all
    default folders to test folders
    """

    clean_settings(monkeypatch, tmp_path)

    tsettings = Settings()

    return tsettings


@pytest.fixture
def tsettings_test(clean_settings, tmp_path, monkeypatch):
    """
    Create a default test settings instance and change all
    default folders to test folders
    """

    clean_settings(monkeypatch, tmp_path)

    # Roaming false
    monkeypatch.setenv("APP_ROAMING", "false")

    tsettings = Settings(log_level="DEBUG", environment="test")

    return tsettings


@pytest.fixture
def tsettings_prod(clean_settings, tmp_path, monkeypatch):
    """
    Create a default test settings instance and change all
    default folders to test folders
    """
    clean_settings(monkeypatch, tmp_path)

    tsettings = Settings(log_level="DEBUG", environment="prod")

    return tsettings


@pytest.fixture
def assert_dirs_empty():
    def _check(settings: Settings):
        assert list(settings.cache_dir.iterdir()) == []
        assert list(settings.logs_dir.iterdir()) == []
        assert list(settings.config_dir.iterdir()) == []

    return _check


@pytest.fixture
def write_env(tmp_path: Path):
    def write(tmp: Path, content: str) -> Path:
        env_path = tmp / ".env"
        env_path.write_text(content, encoding="utf-8")

        return env_path

    return write
