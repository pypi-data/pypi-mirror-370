from pathlib import Path

from build import ProjectBuilder
from packaging.metadata import Metadata
from packaging.requirements import Requirement
from packaging.version import Version


def test_project0(module_data: Path, tmp_path: Path) -> None:
    builder = ProjectBuilder(module_data / "project0")
    metadata_dir = builder.metadata_path(tmp_path)
    metadata_path = Path(metadata_dir) / "METADATA"
    assert metadata_path.is_file()
    metadata = Metadata.from_email(metadata_path.read_bytes())
    assert metadata.name == "addon-odoo-project0", "Lib name if empty is auto computed with 'addon-odoo-' prefix"
    assert set(metadata.classifiers) == {
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Framework :: Odoo",
        "Framework :: Odoo :: 18.0",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    }
    assert metadata.version == Version("18.0.1.2.3")
    assert metadata.license_expression == "AGPL-3.0"
    assert metadata.project_urls["Homepage"] == "https://website.fr"
    assert metadata.author == "Author"
    assert not metadata.author_email
    assert metadata.requires_dist == [Requirement("requests>=2.32")]


def test_project1(module_data: Path, tmp_path: Path) -> None:
    builder = ProjectBuilder(module_data / "project1")
    metadata_dir = builder.metadata_path(tmp_path)
    metadata_path = Path(metadata_dir) / "METADATA"
    assert metadata_path.is_file()
    metadata = Metadata.from_email(metadata_path.read_bytes())
    assert metadata.name == "addon-odoo-project1", "Lib name if empty is auto computed with 'addon-odoo-' prefix"
    assert set(metadata.requires_dist) == {
        Requirement("requests>=2.32"),
    }
    assert set(metadata.classifiers) == {
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Framework :: Odoo",
        "Framework :: Odoo :: 18.0",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    }
    assert metadata.version == Version("18.0.1.2.3")
    assert metadata.license_expression == "AGPL-3.0"
    assert metadata.project_urls["Homepage"] == "https://website.fr"


def test_project2(module_data: Path, tmp_path: Path) -> None:
    builder = ProjectBuilder(module_data / "project2")
    metadata_dir = builder.metadata_path(tmp_path)
    metadata_path = Path(metadata_dir) / "METADATA"
    assert metadata_path.is_file()
    metadata = Metadata.from_email(metadata_path.read_bytes())
    dependencies = set(metadata.requires_dist)
    assert dependencies == {
        Requirement("requests>=2.32"),
        Requirement('odoo-addon-queue-job>=18.0; extra == "queue"'),
        Requirement('pytest; extra == "dev"'),
        Requirement('pytest-cov; extra == "dev"'),
    }
    assert metadata.name == "company-addon-project"
    assert set(metadata.classifiers) == {
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Framework :: Odoo",
        "Framework :: Odoo :: 18.0",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Software Development :: Build Tools",
    }
    assert metadata.version == Version("18.0.1.2.3")
    assert metadata.license_expression == "AGPL-3.0"
    assert metadata.project_urls["Homepage"] == "https://mangono.fr"
