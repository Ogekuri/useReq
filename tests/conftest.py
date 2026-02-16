"""Fixtures pytest condivise per la test suite di source_analyzer."""

import os
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
