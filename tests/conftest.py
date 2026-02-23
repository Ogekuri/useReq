"""Fixtures pytest condivise per la test suite di source_analyzer."""

import os
import shutil
import uuid
from pathlib import Path

import pytest

from usereq.source_analyzer import SourceAnalyzer


@pytest.fixture(scope="session")
def analyzer():
    """Istanza condivisa dell'analyzer."""
    return SourceAnalyzer()


@pytest.fixture(scope="session")
def fixtures_dir():
    """Percorso della directory fixtures."""
    return os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(scope="session")
def temp_output_dir():
    """Percorso output temporaneo test sotto temp/."""
    path = os.path.join(os.path.dirname(__file__), "..", "temp", "tests")
    os.makedirs(path, exist_ok=True)
    return path


@pytest.fixture
def repo_temp_dir():
    """Return a unique per-test directory under repository temp/tests/."""
    base = (Path(__file__).resolve().parents[1] / "temp" / "tests").resolve()
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"pytest-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
