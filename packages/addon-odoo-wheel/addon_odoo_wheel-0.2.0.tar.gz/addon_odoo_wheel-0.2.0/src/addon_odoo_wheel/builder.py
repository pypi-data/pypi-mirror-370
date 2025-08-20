"""
This module provides functionality to build wheels and source distributions (sdists)
for Odoo addons, following PEP 517 and PEP 660.

- [PEP 517](https://peps.python.org/pep-0517/): A standard for specifying build backends.
- [PEP 660](https://peps.python.org/pep-0660/): A standard for creating editable wheels.
"""

from __future__ import annotations

import logging
import os
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Any

from wheel.wheelfile import WheelFile

from . import utils
from .metadata import AddonMetadata

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


class AddonBuilder:
    def __init__(self, distribution_addon_dir: Path, config: dict):
        force_addon_name = None
        if (distribution_addon_dir / "odoo-addon-name.txt").exists():
            with (distribution_addon_dir / "odoo-addon-name.txt").open("r") as f:
                force_addon_name = f.read()
        self.addon_metadata = AddonMetadata.from_addon_dir(
            distribution_addon_dir, allow_not_installable=True, force_addon_name=force_addon_name
        )
        self.config = config
        self.addon_dir = distribution_addon_dir

    def build_sdist_to(self, sdist_directory: Path) -> str:
        sdist_tar_name = self.addon_metadata.sdist_name + ".tar.gz"
        with tempfile.TemporaryDirectory() as tmpdir:
            sdist_tmpdir = Path(tmpdir) / self.addon_metadata.sdist_name
            utils.copy_to(
                self.addon_metadata.addon_path,
                sdist_tmpdir,
                pkg_exclude=self.addon_metadata.module_contributor.pkg_exclude("sdist"),
            )
            utils.write_metadata(self.addon_metadata.metadata, dest=sdist_tmpdir / "PKG-INFO")
            (sdist_tmpdir / "odoo-addon-name.txt").write_text(self.addon_metadata.addon_name)
            with tarfile.open(
                str(sdist_directory / sdist_tar_name),
                mode="w|gz",
                format=tarfile.PAX_FORMAT,
            ) as tf:
                tf.add(str(sdist_tmpdir), arcname=self.addon_metadata.sdist_name)
        return sdist_tar_name

    def make_dist_info(self, dst: Path) -> str:
        dist_info_dirname = f"{self.addon_metadata.sdist_name}.dist-info"
        dist_info_path = dst / dist_info_dirname
        dist_info_path.mkdir()
        utils.write_metadata(utils.base_wheel_metadata(), dest=dist_info_path / "WHEEL")
        utils.write_metadata(self.addon_metadata.metadata, dest=dist_info_path / "METADATA")
        (dist_info_path / "top_level.txt").write_text("odoo")
        entry_points = self.addon_metadata.pyproject_options.entry_points
        if not entry_points:
            entry_points = self.addon_metadata.pyproject_options.addon_odoo_wheel.entry_points
        utils.create_entry_point(
            entry_points, python_addon_path=self.addon_metadata.python_addon_path, dest=dist_info_path
        )
        return dist_info_dirname

    def build_wheel_to(self, wheel_directory: Path, *, editable: bool = False) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # always include metadata
            self.make_dist_info(tmppath)
            if editable:
                # Prepare {addon_dir}/build/__editable__/odoo/addon/{addon_name} symlink
                self._make_wheel_editable(tmppath)
            else:
                self._make_static_wheel(tmppath)

            wheel_path = os.path.join(wheel_directory, self.addon_metadata.wheel_name + ".whl")
            with WheelFile(wheel_path, "w") as wf:
                _logger.info(f"Repacking wheel as {wheel_path}...")
                wf.write_files(str(tmppath.absolute()))
        return self.addon_metadata.wheel_name + ".whl"

    def _make_static_wheel(self, tmppath):
        odoo_addon_path = tmppath / "odoo" / "addons"
        odoo_addon_path.mkdir(parents=True)
        odoo_addon_path = odoo_addon_path / self.addon_metadata.addon_name
        utils.copy_to(
            self.addon_metadata.addon_path,
            odoo_addon_path,
            pkg_exclude=self.addon_metadata.module_contributor.pkg_exclude("whl"),
        )
        # we don't want pyproject.toml nor PKG-INFO in the wheel
        utils.ensure_absent(
            [
                odoo_addon_path / "pyproject.toml",
                odoo_addon_path / "PKG-INFO",
                odoo_addon_path / "odoo-addon-name.txt",
                odoo_addon_path / "requirements.txt",
            ]
        )

    def _make_wheel_editable(self, tmppath: Path):
        build_dir = self.addon_metadata.addon_path / "build"
        build_dir.mkdir(parents=True, exist_ok=True)
        build_dir.joinpath(".gitignore").write_text("*")
        editable_dir = build_dir / "__editable__"
        if editable_dir.is_dir():
            shutil.rmtree(editable_dir)
        editable_addons_dir = editable_dir / "odoo" / "addons"
        editable_addons_dir.mkdir(parents=True, exist_ok=True)
        editable_addon_symlink = editable_addons_dir / self.addon_metadata.addon_name
        editable_addon_symlink.symlink_to(self.addon_metadata.addon_path, target_is_directory=True)
        # Add .pth file pointing to {addon_dir}/build/__editable__ into the wheel
        tmppath.joinpath(self.addon_metadata.metadata["Name"] + ".pth").write_text(str(editable_dir.resolve()))


def build_wheel(
    wheel_directory: str, config_settings: dict[str, Any] | None = None, metadata_directory: str | None = None
) -> str:
    """
    Build a wheel for the Odoo addon.
    Following PEP 517

    This function creates a non-editable wheel for the Odoo addon present in the
    current working directory. It utilizes the AddonWheelBuilder to perform the
    build process.

    Args:
        wheel_directory (str): The directory where the built wheel will be stored.
        config_settings (Optional[Dict[str, Any]]): Optional configuration settings
            for the build process. Defaults to None.
        metadata_directory (Optional[str]): Optional directory for metadata.
            Defaults to None.

    Returns:
        str: The name of the built wheel file.
    """
    return AddonBuilder(Path.cwd(), config_settings).build_wheel_to(Path(wheel_directory), editable=False)


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    """
    Build an editable wheel for the Odoo addon.

    Following PEP 660 (editable wheels)

    This function creates an editable wheel for the Odoo addon present in the
    current working directory. It utilizes the AddonWheelBuilder to perform the
    build process.

    Args:
        wheel_directory (str): The directory where the built wheel will be stored.
        config_settings (Optional[Dict[str, Any]]): Optional configuration settings
            for the build process. Defaults to None.
        metadata_directory (Optional[str]): Optional directory for metadata.
            Defaults to None.

    Returns:
        str: The name of the built wheel file.
    """
    return AddonBuilder(Path.cwd(), config_settings).build_wheel_to(Path(wheel_directory), editable=True)


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings: dict[str, Any] | None = None) -> str:
    """
    Prepare the metadata for a wheel build.

    Following PEP 517

    This function creates the necessary metadata for a wheel build of the Odoo addon
    present in the current working directory. It utilizes the package_metadata_from_addon
    function to create the metadata and the _make_dist_info function to write the metadata
    to disk.

    Args:
        metadata_directory (str): The directory where the metadata will be stored.
        config_settings (Optional[Dict[str, Any]]): Optional configuration settings
            for the build process. Defaults to None.

    Returns:
        str: The name of the .dist-info directory created.
    """
    return AddonBuilder(Path.cwd(), config_settings).make_dist_info(Path(metadata_directory))


prepare_metadata_for_build_editable = prepare_metadata_for_build_wheel


def build_sdist(sdist_directory: str, config_settings: dict[str, Any] | None = None) -> str:
    """
    Build a source distribution (sdist) for the Odoo addon.

    Following PEP 517

    This function creates an sdist for the Odoo addon present in the
    current working directory. It utilizes the _build_sdist function to perform the
    build process.

    Args:
        sdist_directory (str): The directory where the built sdist will be stored.
        config_settings (Optional[Dict[str, Any]]): Optional configuration settings
            for the build process. Defaults to None.

    Returns:
        str: The name of the built sdist file.
    """
    return AddonBuilder(Path.cwd(), config_settings).build_sdist_to(Path(sdist_directory))
