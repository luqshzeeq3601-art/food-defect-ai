"""Global pytest fixtures and configuration for Food Defect AI test suite."""

import sys
from pathlib import Path

import pytest

# Ensure repository root is always at the head of sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return BASE_DIR


@pytest.fixture(scope="session")
def samples_dir(project_root: Path) -> Path:
    """Return the absolute path to the data/samples test fixtures directory."""
    return project_root / "data" / "samples"


@pytest.fixture(scope="session")
def sample_defective_fruit_path(samples_dir: Path) -> Path:
    """Return path to standard defective fruit test sample."""
    return samples_dir / "dataset_defective_fruit.jpg"


@pytest.fixture(scope="session")
def sample_healthy_fruit_path(samples_dir: Path) -> Path:
    """Return path to standard healthy fruit test sample."""
    return samples_dir / "dataset_healthy_fruit.jpg"


@pytest.fixture(scope="session")
def sample_empty_conveyor_path(samples_dir: Path) -> Path:
    """Return path to empty conveyor negative test sample."""
    return samples_dir / "negative_backgrounds" / "conveyor_empty_01.jpg"
