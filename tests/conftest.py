import pytest

from tomatempo.settings import Settings


@pytest.fixture
def tsettings_test(tmp_path, monkeypatch):
    """
    Create a default test settings instance and change all
    default folders to test folders
    """
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_LOGS_HOME", str(tmp_path / "logs"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    tsettings = Settings(log_level="DEBUG", environment="test")

    return tsettings


@pytest.fixture
def tsettings_prod(tmp_path, monkeypatch):
    """
    Create a default test settings instance and change all
    default folders to test folders
    """
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_LOGS_HOME", str(tmp_path / "logs"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    tsettings = Settings(log_level="DEBUG", environment="prod")

    return tsettings


@pytest.fixture
def assert_dirs_empty():
    def _check(settings: Settings):
        assert list(settings.cache_dir.iterdir()) == []
        assert list(settings.logs_dir.iterdir()) == []
        assert list(settings.config_dir.iterdir()) == []

    return _check
