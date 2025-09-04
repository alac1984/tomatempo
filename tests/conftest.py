import logging
import os
from pathlib import Path

import pytest
from freezegun import freeze_time

from tomatempo.logs import JSONFormatter
from tomatempo.settings import Settings, get_settings


@pytest.fixture
def clean_settings(tmp_path):
    """
    Limpa variáveis de ambiente e ajusta diretórios temporários
    para garantir um ambiente controlado nos testes.
    """

    def clean(m: pytest.MonkeyPatch, tmp: Path) -> None:
        # Limpa variáveis XDG
        m.delenv("XDG_CONFIG_HOME", raising=False)
        m.delenv("XDG_STATE_HOME", raising=False)
        m.delenv("XDG_CACHE_HOME", raising=False)

        # Limpa variáveis de ambiente da aplicação
        for v in list(os.environ):
            if v.startswith("APP_"):
                m.delenv(v, raising=False)

        # Define novo diretório de trabalho
        m.chdir(tmp)

        # Cria novos diretórios base
        m.setenv("XDG_CONFIG_HOME", str(tmp / "config"))
        m.setenv("XDG_STATE_HOME", str(tmp / "state"))
        m.setenv("XDG_CACHE_HOME", str(tmp / "cache"))

        # Limpa o cache da singleton
        get_settings.cache_clear()

        # Remove arquivo .env, se existir
        (tmp / ".env").unlink(missing_ok=True)

    return clean


@pytest.fixture
def tsettings(clean_settings, tmp_path, monkeypatch):
    """
    Cria uma instância padrão de Settings com diretórios de teste.
    """
    clean_settings(monkeypatch, tmp_path)
    return Settings()


@pytest.fixture
def tsettings_test(clean_settings, tmp_path, monkeypatch):
    """
    Cria uma instância de Settings em ambiente de teste,
    com APP_ROAMING = false.
    """
    clean_settings(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_ROAMING", "false")
    return Settings(log_level="DEBUG", environment="test")


@pytest.fixture
def tsettings_prod(clean_settings, tmp_path, monkeypatch):
    """
    Cria uma instância de Settings em ambiente de produção.
    """
    clean_settings(monkeypatch, tmp_path)
    return Settings(log_level="DEBUG", environment="prod")


@pytest.fixture
def assert_dirs_empty():
    """
    Verifica se os diretórios de cache, logs e config estão vazios.
    """

    def _check(settings: Settings):
        assert list(settings.cache_dir.iterdir()) == []
        assert list(settings.logs_dir.iterdir()) == []
        assert list(settings.config_dir.iterdir()) == []
        return _check

    return _check


@pytest.fixture
def write_env(tmp_path: Path):
    """
    Cria um arquivo `.env` no diretório temporário com o conteúdo fornecido.
    """

    def write(tmp: Path, content: str) -> Path:
        env_path = tmp / ".env"
        env_path.write_text(content, encoding="utf-8")
        return env_path

    return write


@pytest.fixture
def log_record(tmp_path):
    with freeze_time("2023-01-01 12:00:00"):
        yield logging.LogRecord(
            "test", 10, str(tmp_path), 10, "This is a test", None, None, test_field="Test field"
        )


@pytest.fixture
def json_formatter():
    format_keys = {
        "level": "levelname",
        "message": "message",
        "timestamp": "timestamp",
        "logger": "name",
        "module": "module",
        "function": "funcName",
        "line": "lineno",
        "thread_name": "threadName",
    }

    return JSONFormatter(fmt_keys=format_keys)
