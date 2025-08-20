import os
from pathlib import Path
from zipfile import ZipFile

from addon_odoo_wheel.builder import build_editable

from .utils import dir_changer


def test_build_editable(project0: Path, tmp_path: Path) -> None:
    with dir_changer(project0):
        wheel_name = build_editable(os.fspath(tmp_path))
        # test build directory content
        build_dir = project0 / "build"
        assert build_dir.is_dir()
        assert build_dir.joinpath(".gitignore").is_file()
        editable_dir = build_dir / "__editable__"
        editable_manifest_path = editable_dir / "odoo" / "addons" / "project0" / "__manifest__.py"
        assert editable_manifest_path.is_file()
        # test wheel contenet
        assert (tmp_path / wheel_name).exists()
        with ZipFile(tmp_path / wheel_name) as zf:
            names = zf.namelist()
            assert "odoo/addons/project0/__manifest__.py" not in names
            assert "addon-odoo-project0.pth" in names
            assert zf.open("addon-odoo-project0.pth", "r").read().decode("utf-8") == str(editable_dir.resolve())
