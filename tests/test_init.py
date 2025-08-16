import pytest
from typer.testing import CliRunner


@pytest.mark.smoke
def test_smoke_imports_tomatempo_test(tsettings_test, assert_dirs_empty):
    assert_dirs_empty(tsettings_test)


@pytest.mark.smoke
def test_smoke_imports_tomatempo_prod(tsettings_prod, assert_dirs_empty):
    assert_dirs_empty(tsettings_prod)


@pytest.mark.smoke
def test_smoke_imports_app_test(tsettings_test, assert_dirs_empty):
    assert_dirs_empty(tsettings_test)


@pytest.mark.smoke
def test_smoke_imports_app_prod(tsettings_prod, assert_dirs_empty):
    assert_dirs_empty(tsettings_prod)


@pytest.mark.smoke
def test_smoke_imports_help(tsettings_test):
    from tomatempo.cli import app

    runner = CliRunner()

    result = runner.invoke(app, ["tomatempo", "--help"])

    assert result.exit_code == 0
    assert "Arguments" in result.output
