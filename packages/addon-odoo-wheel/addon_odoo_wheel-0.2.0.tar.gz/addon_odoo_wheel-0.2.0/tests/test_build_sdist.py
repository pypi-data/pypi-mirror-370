import os
from pathlib import Path
from tarfile import TarFile

from addon_odoo_wheel.builder import AddonBuilder, build_sdist

from .utils import dir_changer


def test_build_sdist(project0: Path, tmp_path: Path) -> None:
    with dir_changer(project0):
        sdist_name = build_sdist(os.fspath(tmp_path))
        assert sdist_name == "addon_odoo_project0-18.0.1.2.3.tar.gz"
        assert (tmp_path / sdist_name).exists()


def test_build_sdist_from_sdist(addon1_sdist_builder: AddonBuilder, tmp_path: Path) -> None:
    assert addon1_sdist_builder.addon_metadata.sdist_name == "company_addon_project-18.0.1.2.3"
    sdist_name = addon1_sdist_builder.build_sdist_to(tmp_path)
    assert sdist_name == "company_addon_project-18.0.1.2.3.tar.gz"
    # extract sdist and test that the root directory has the correct name

    tmp_path2 = tmp_path / "2"
    tmp_path2.mkdir()
    with TarFile.open(tmp_path / sdist_name, mode="r:gz") as tf1:
        tf1_names = sorted(tf1.getnames())
        tf1.extractall(tmp_path2)
    assert "company_addon_project-18.0.1.2.3/PKG-INFO" in tf1_names
    assert "company_addon_project-18.0.1.2.3/pyproject.toml" in tf1_names
    # build sdist from sdist
    tmp_path3 = tmp_path / "3"
    tmp_path3.mkdir()
    sdist_name = AddonBuilder(
        tmp_path2 / "company_addon_project-18.0.1.2.3", addon1_sdist_builder.config
    ).build_sdist_to(tmp_path3)
    assert sdist_name == "company_addon_project-18.0.1.2.3.tar.gz"
    # extract 2nd sdist and test that the root directory has the correct name
    with TarFile.open(tmp_path3 / sdist_name, mode="r:gz") as tf2:
        tf2_names = sorted(tf2.getnames())
        tf2.extractall(tmp_path3)
    # content of both sdists must be identical
    assert tf1_names == tf2_names
    # PKG-INFO in both sdists must be identical
    assert (tmp_path2 / "company_addon_project-18.0.1.2.3" / "PKG-INFO").read_bytes() == (
        tmp_path3 / "company_addon_project-18.0.1.2.3" / "PKG-INFO"
    ).read_bytes()
