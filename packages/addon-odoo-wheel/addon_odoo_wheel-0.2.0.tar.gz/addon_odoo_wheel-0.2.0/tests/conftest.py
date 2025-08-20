from pathlib import Path

import pytest

from addon_odoo_wheel import builder


@pytest.fixture
def addon1_sdist_builder(project2: Path) -> builder.AddonBuilder:
    return builder.AddonBuilder(project2, {})


@pytest.fixture
def module_data() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent.joinpath("data")


@pytest.fixture(scope="session")
def project0(data_path: Path) -> Path:
    return data_path / "project0"


@pytest.fixture(scope="session")
def project1(data_path: Path) -> Path:
    return data_path / "project1"


@pytest.fixture(scope="session")
def project2(data_path: Path) -> Path:
    return data_path / "project2"
