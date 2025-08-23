from platform import system

import pytest
from pydantic import ValidationError

from tomatempo.settings import Settings, get_settings, reload_settings

# ---------------------------
# Construction & Defaults
# ---------------------------


def test_settings_defaults(tsettings):
    """
    Ensure that without env vars or kwargs, the instance uses the
    default values defined in the class.
    """

    assert tsettings is not None
    assert tsettings.app_name == "tomatempo"
    assert tsettings.app_author == "André Carvalho"
    assert tsettings.roaming
    assert tsettings.ensure_dirs
    assert tsettings.environment == "dev"
    assert tsettings.log_level == "INFO"
    assert tsettings.database_url == "sqlite:///./data.db"
    assert tsettings.log_level_numeric == 20
    assert tsettings.is_prod is False
    if system() == "Linux":
        assert tsettings.config_dir.name == "tomatempo"
        assert tsettings.config_dir.parent.name == "config"
    elif system() == "Darwin":
        assert tsettings.config_dir.name == "tomatempo"
        assert tsettings.config_dir.parent.name == "Application Support"
    elif system() == "Windows":
        assert tsettings.config_dir.name == "tomatempo"
        assert "AppData" in str(tsettings.config_dir.parent)


def test_settings_from_kwargs(tsettings_test):
    """Ensure that values passed via kwargs (Settings(environment="test")) override the defaults."""

    assert tsettings_test.environment == "test"
    assert tsettings_test.log_level == "DEBUG"
    assert tsettings_test.log_level_numeric == 10
    assert tsettings_test.is_prod is False
    assert tsettings_test.debug is True


def test_settings_from_env(clean_settings, tmp_path, monkeypatch):
    """
    Ensure that environment variables with prefix APP_ (e.g., APP_ENVIRONMENT)
    are correctly loaded."""

    clean_settings(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_ENVIRONMENT", "prod")
    monkeypatch.setenv("APP_LOG_LEVEL", "warning")  # Testing case insensitive
    monkeypatch.setenv("APP_DATABASE_URL", "sqlite:///env.db")
    monkeypatch.setenv("APP_ROAMING", "false")
    monkeypatch.setenv("APP_ENSURE_DIRS", "0")

    settings = Settings()

    assert settings.environment == "prod"
    assert settings.log_level == "WARNING"
    assert settings.database_url == "sqlite:///env.db"
    assert settings.roaming is False
    assert settings.ensure_dirs is False
    assert settings.log_level_numeric == 30
    assert settings.is_prod is True
    assert settings.debug is False


def test_settings_precedence(clean_settings, tmp_path, write_env, monkeypatch):
    """Ensure the precedence order is kwargs > env vars > .env > defaults."""

    # Changing all of them, kwargs should win
    clean_settings(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_LOG_LEVEL", "WARNING")
    write_env(tmp_path, "APP_LOG_LEVEL=ERROR\n")
    settings = Settings(log_level="DEBUG")

    assert settings.log_level == "DEBUG"

    # Changing env vars and .env, env vars should win
    clean_settings(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_LOG_LEVEL", "WARNING")
    write_env(tmp_path, "APP_LOG_LEVEL=ERROR\n")
    settings = Settings()

    assert settings.log_level == "WARNING"

    # Changing .env, .env should win
    clean_settings(monkeypatch, tmp_path)
    write_env(tmp_path, "APP_LOG_LEVEL=ERROR\n")
    settings = Settings()

    assert settings.log_level == "ERROR"

    # Changing none, defaults should win
    clean_settings(monkeypatch, tmp_path)
    settings = Settings()

    assert settings.log_level == "INFO"


# ---------------------------
# Validation
# ---------------------------


def test_invalid_log_level_raises():
    """Ensure that an invalid log_level raises a ValueError in the validator."""

    with pytest.raises(ValidationError, match="invalid log_level"):
        Settings(log_level="testing")


def test_invalid_environment_raises():
    """Ensure that an invalid environment raises a ValueError in the validator."""

    with pytest.raises(ValidationError, match="invalid environment"):
        Settings(environment="stages")


# ---------------------------
# Computed Fields
# ---------------------------


def test_log_level_numeric_mapping(clean_settings, monkeypatch, tmp_path):
    """Confirm that log_level_numeric returns the correct numeric value for each log level."""

    clean_settings(monkeypatch, tmp_path)

    s1 = Settings(log_level="DEBUG")
    s2 = Settings(log_level="INFO")
    s3 = Settings(log_level="WARNING")
    s4 = Settings(log_level="ERROR")
    s5 = Settings(log_level="CRITICAL")

    assert s1.log_level_numeric == 10
    assert s2.log_level_numeric == 20
    assert s3.log_level_numeric == 30
    assert s4.log_level_numeric == 40
    assert s5.log_level_numeric == 50


def test_is_prod_true_only_in_prod(clean_settings, monkeypatch, tmp_path):
    """Confirm that is_prod is True only when environment='prod'."""

    clean_settings(monkeypatch, tmp_path)

    s1 = Settings(environment="dev")
    s2 = Settings(environment="staging")
    s3 = Settings(environment="test")
    s4 = Settings(environment="prod")

    assert not s1.is_prod
    assert not s2.is_prod
    assert not s3.is_prod
    assert s4.is_prod


def test_environment_case_insensitive(clean_settings, tmp_path, monkeypatch):
    clean_settings(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_ENVIRONMENT", "PROD")
    s = Settings()
    assert s.environment == "prod"


def test_debug_true_in_dev_and_test(clean_settings, monkeypatch, tmp_path):
    """Confirm that debug is True only in dev and test, and False in prod and staging."""

    clean_settings(monkeypatch, tmp_path)

    s1 = Settings(environment="dev")
    s2 = Settings(environment="staging")
    s3 = Settings(environment="test")
    s4 = Settings(environment="prod")

    assert s1.debug
    assert not s2.debug
    assert s3.debug
    assert not s4.debug


# ---------------------------
# Directories
# ---------------------------


def test_cache_dir_created(clean_settings, monkeypatch, tmp_path):
    """Ensure that cache_dir creates the directory if ensure_dirs=True."""

    clean_settings(monkeypatch, tmp_path)

    settings = Settings(ensure_dirs=True)

    assert settings.cache_dir.exists()


def test_logs_dir_created(clean_settings, monkeypatch, tmp_path):
    """Ensure that logs_dir creates the directory if ensure_dirs=True."""

    clean_settings(monkeypatch, tmp_path)

    settings = Settings(ensure_dirs=True)

    assert settings.logs_dir.exists()


def test_config_dir_created(clean_settings, monkeypatch, tmp_path):
    """Ensure that config_dir creates the directory if ensure_dirs=True."""

    clean_settings(monkeypatch, tmp_path)

    settings = Settings(ensure_dirs=True)

    assert settings.config_dir.exists()


def test_dirs_not_created_if_disabled(clean_settings, monkeypatch, tmp_path):
    """Ensure that if ensure_dirs=False, the directories are not created automatically."""

    clean_settings(monkeypatch, tmp_path)

    settings = Settings(ensure_dirs=False)

    assert not settings.cache_dir.exists()
    assert not settings.logs_dir.exists()
    assert not settings.config_dir.exists()


# ---------------------------
# Singleton
# ---------------------------


def test_get_settings_singleton(clean_settings, monkeypatch, tmp_path):
    """Ensure that get_settings() always returns the same instance while the cache is not cleared."""

    clean_settings(monkeypatch, tmp_path)

    settings1 = get_settings()

    settings1.log_level = "WARNING"

    settings2 = get_settings()

    assert settings1 is settings2


def test_env_change_requires_reload(clean_settings, tmp_path, monkeypatch):
    clean_settings(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_LOG_LEVEL", "INFO")
    s1 = get_settings()
    assert s1.log_level == "INFO"

    # muda env
    monkeypatch.setenv("APP_LOG_LEVEL", "ERROR")
    s_still = get_settings()
    assert s_still.log_level == "INFO"  # ainda o mesmo singleton

    s2 = reload_settings()
    assert s2.log_level == "ERROR"
    assert s2 is get_settings()


def test_reload_settings_creates_new_instance(clean_settings, monkeypatch, tmp_path):
    """Ensure that reload_settings() clears the cache and returns a new distinct instance."""
    # TODO

    clean_settings(monkeypatch, tmp_path)

    settings1 = get_settings()

    settings1.log_level = "WARNING"

    settings2 = reload_settings()

    assert settings1 is not settings2
