import os

import pytest
from typer.testing import CliRunner

pytestmark = pytest.mark.usefixtures("_side_effects")


@pytest.mark.smoke
def test_smoke_imports_tomatempo():
    assert os.listdir(os.getcwd()) == []


@pytest.mark.smoke
def test_smoke_imports_app():
    assert os.listdir(os.getcwd()) == []


@pytest.mark.smoke
def test_smoke_imports_help():
    from tomatempo.cli import app

    runner = CliRunner()

    result = runner.invoke(app, ["tomatempo", "--help"])

    assert result.exit_code == 0
    assert "Arguments" in result.output
