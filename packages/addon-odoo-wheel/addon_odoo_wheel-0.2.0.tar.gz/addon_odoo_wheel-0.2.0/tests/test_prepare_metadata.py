import os
from pathlib import Path

from addon_odoo_wheel.builder import (
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

from .utils import dir_changer


def test_prepare_metadata_for_build_wheel(project2: Path, tmp_path: Path) -> None:
    with dir_changer(project2):
        dist_info_dir = prepare_metadata_for_build_wheel(os.fspath(tmp_path))
        assert dist_info_dir == "company_addon_project-18.0.1.2.3.dist-info"
        dist_info_path = tmp_path / dist_info_dir
        assert dist_info_path.is_dir()
        metadata_path = dist_info_path / "METADATA"
        assert metadata_path.is_file()


def test_prepare_metadata_for_build_editable(project2: Path, tmp_path: Path) -> None:
    with dir_changer(project2):
        dist_info_dir = prepare_metadata_for_build_editable(os.fspath(tmp_path))
        assert dist_info_dir == "company_addon_project-18.0.1.2.3.dist-info"
        dist_info_path = tmp_path / dist_info_dir
        assert dist_info_path.is_dir()
        metadata_path = dist_info_path / "METADATA"
        assert metadata_path.is_file()
