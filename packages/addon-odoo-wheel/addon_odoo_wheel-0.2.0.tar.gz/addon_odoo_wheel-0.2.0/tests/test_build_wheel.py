import os
from pathlib import Path
from zipfile import ZipFile

import pytest
from manifestoo_core.git_postversion import POST_VERSION_STRATEGY_NONE
from whool.init import init_addon_dir

from addon_odoo_wheel.builder import build_wheel

from .utils import dir_changer


def test_build_wheel(module_data: Path, tmp_path: Path) -> None:
    with dir_changer(module_data / "module1"):
        wheel_name = build_wheel(os.fspath(tmp_path))
        assert wheel_name == "awesome_odoo_addon-15.0.1.0.0-py3-none-any.whl"
        assert (tmp_path / wheel_name).exists()
        with ZipFile(tmp_path / wheel_name) as zf:
            names = zf.namelist()
            assert "odoo/addons/module1/__manifest__.py" in names
            assert "odoo/addons/module1/pyproject.toml" not in names


def test_build_wheel_without_scm(tmp_path: Path) -> None:
    addon_dir = tmp_path / "addon1"
    addon_dir.mkdir()
    addon_dir.joinpath("__manifest__.py").write_text("{'name': 'addon1', 'version': '16.0.1.0.0'}")
    addon_dir.joinpath("__init__.py").touch()
    init_addon_dir(addon_dir)
    wheel_path = tmp_path / "wheel"
    wheel_path.mkdir()
    with dir_changer(addon_dir):
        wheel_name = build_wheel(os.fspath(wheel_path))
        assert wheel_name == "addon_odoo_addon1-16.0.1.0.0-py3-none-any.whl"
        assert (wheel_path / wheel_name).exists()
        with ZipFile(wheel_path / wheel_name) as zf:
            names = zf.namelist()
            assert "odoo/addons/addon1/__manifest__.py" in names
            assert "odoo/addons/addon1/pyproject.toml" not in names


def test_build_wheel_git_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Make sure we can't find git executable
    monkeypatch.setenv("PATH", "/foo")
    # Override strategy so Git is not needed
    monkeypatch.setenv("WHOOL_POST_VERSION_STRATEGY_OVERRIDE", POST_VERSION_STRATEGY_NONE)
    test_build_wheel_without_scm(tmp_path)
