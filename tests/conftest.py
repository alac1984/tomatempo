import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture
def _side_effects(monkeypatch):
    # Change current working dir
    temp_dir = Path(".tests/")

    # Pointing all other dirs to temp_dir

    # If temp_dir exists
    if not temp_dir.exists():
        os.mkdir(temp_dir)
    else:
        shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)

    monkeypatch.chdir(temp_dir)

    yield

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
