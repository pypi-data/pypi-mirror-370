from __future__ import annotations

import configparser
import logging
import os
import re
import shutil
import string
import subprocess
import typing
from email.generator import Generator
from email.message import Message
from pathlib import Path
from typing import Any, Callable

from manifestoo_core.metadata import EXTERNAL_DEPENDENCIES_MAP
from packaging.requirements import Requirement
from typing_extensions import TypeAlias

from .compat import tomllib
from .exceptions import NoScmFound
from .version import version as lib_version

_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    pass


def _get_mapping_metadata():
    return {"-".join(t.capitalize() for t in k.split("-")): v for k, v in EXTERNAL_DEPENDENCIES_MAP.items()}


EXTRA_NAME_RE = re.compile("^[a-z0-9]+(-[a-z0-9]+)*$")

CORE_METADATA_PROJECT_FIELDS = {
    "Author": ("authors",),
    "Author-email": ("authors",),
    "Classifier": ("classifiers",),
    "Description": ("readme",),
    "Description-Content-Type": ("readme",),
    "Dynamic": ("dynamic",),
    "Keywords": ("keywords",),
    "License": ("license",),
    "License-Expression": ("license",),
    "License-Files": ("license-files",),
    "Maintainer": ("maintainers",),
    "Maintainer-email": ("maintainers",),
    "Name": ("name",),
    "Provides-Extra": ("dependencies", "optional-dependencies"),
    "Requires-Dist": ("dependencies",),
    "Requires-Python": ("requires-python",),
    "Summary": ("description",),
    "Project-URL": ("urls",),
    "Version": ("version",),
}
PROJECT_CORE_METADATA_FIELDS = {
    "authors": ("Author", "Author-email"),
    "classifiers": ("Classifier",),
    "dependencies": ("Requires-Dist",),
    "dynamic": ("Dynamic",),
    "keywords": ("Keywords",),
    "license": ("License", "License-Expression"),
    "license-files": ("License-Files",),
    "maintainers": ("Maintainer", "Maintainer-email"),
    "name": ("Name",),
    "optional-dependencies": ("Requires-Dist", "Provides-Extra"),
    "readme": ("Description", "Description-Content-Type"),
    "requires-python": ("Requires-Python",),
    "description": ("Summary",),
    "urls": ("Project-URL",),
    "version": ("Version",),
}
WHEEL_TAG = "py3-none-any"

"""
Mapping with SDPX licence from https://spdx.org/licenses/
"""
odoo_licence_to_SDPX = {
    "GPL-2": ("GPL-2.0", "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"),
    "GPL-2 or any later version": (
        "GPL-2.0-or-later",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    ),
    "GPL-3": ("GPL-3.0-only", "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"),
    "GPL-3 or any later version": (
        "GPL-3.0-or-later",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ),
    "AGPL-3": (
        "AGPL-3.0",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ),
    "AGPL-3 or any later version": (
        "AGPL-3.0",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    ),
    "LGPL-2": ("LGPL-2.0", "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)"),
    "LGPL-2 or any later version": (
        "LGPL-2.0",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
    ),
    "LGPL-3": ("LGPL-3", "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"),
    "LGPL-3 or any later version": (
        "LGPL-3.0-or-later",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    ),
    "Other OSI approved licence": ("any-OSI", None),
    "OEEL-1": ("LicenseRef-OEEL-1", None),
    "OPL-1": ("LicenseRef-OPL-1", None),
    "Other proprietary": (None, None),
}


def base_wheel_metadata() -> Message:
    """
    Create and return the base metadata for the wheel.

    This metadata includes the wheel version, the generator information,
    whether the root is purelib, and the tag. It is used in the creation
    of the wheel file for the Odoo addon.

    Returns:
        Message: An email.message.Message object containing the base wheel metadata.
    """
    msg = Message()
    msg["Wheel-Version"] = "1.0"  # of the spec
    msg["Generator"] = "Mangono Wheel Builder" + lib_version
    msg["Root-Is-Purelib"] = "true"
    msg["Tag"] = WHEEL_TAG
    return msg


def write_metadata(msg: Message, dest: Path) -> None:
    with open(dest, "w", encoding="utf-8") as f:
        Generator(f, mangle_from_=False, maxheaderlen=0).flatten(msg)


EntryPoints: TypeAlias = typing.Dict[str, typing.Dict[str, str]]


class CaseSensitiveConfigParser(configparser.ConfigParser):
    optionxform = staticmethod(str)


def create_entry_point(entry_points: EntryPoints, python_addon_path: str, dest: Path):
    if not entry_points:
        return
    entrypoint_format = CaseSensitiveConfigParser()
    for entry_key, entry_value in entry_points.items():
        entrypoint_format.add_section(entry_key)
        for entry_name, entry_path in entry_value.items():
            odoo_entry_path = f"{python_addon_path}.{entry_path}"
            if entry_path.startswith(python_addon_path):
                odoo_entry_path = entry_path
            entrypoint_format.set(entry_key, entry_name, odoo_entry_path)
    entrypoint_format.write((dest / "entry_points.txt").open("w"))


def load_pyproject_toml(addon_dir: Path) -> PyProjectConfig:
    pyproject_toml_path = addon_dir / "pyproject.toml"
    if pyproject_toml_path.exists():
        with open(pyproject_toml_path, "rb") as f:
            return PyProjectConfig.from_config(tomllib.load(f))
    return PyProjectConfig.from_config({})


WellKnownLabels = [
    "homepage",
    "source",
    "download",
    "changelog",
    "releasenotes",
    "documentation",
    "issues",
    "funding",
]


def normalize_label(label: str) -> tuple[bool, str]:
    chars_to_remove = string.punctuation + string.whitespace
    removal_map = str.maketrans("", "", chars_to_remove)
    n_label = label.translate(removal_map).lower()
    return n_label in WellKnownLabels, n_label.capitalize()


class PyProjectConfigBase(dict):
    @classmethod
    def from_file(cls, pyproject_toml_path: Path) -> PyProjectConfig:
        if not pyproject_toml_path.exists():
            raise FileNotFoundError(pyproject_toml_path)
        with open(pyproject_toml_path, "rb") as f:
            return cls.from_config(tomllib.load(f))

    @property
    def dependencies(self) -> list[Requirement]:
        return [Requirement(dep) for dep in self.get("dependencies") or []]

    @property
    def optional_dependencies(self) -> dict[str, list[Requirement]]:
        return {
            option: [Requirement(dep) for dep in deps] for option, deps in self.get("optional-dependencies", {}).items()
        }

    @property
    def author(self) -> str | None:
        return self.get("author")

    @property
    def author_email(self) -> str | None:
        return self.get("author_email")

    @property
    def requires_python(self) -> str | None:
        return self.get("requires_python")

    @property
    def classifiers(self) -> list[str]:
        return self.get("classifiers", [])

    @property
    def entry_points(self) -> EntryPoints:
        return self.get("entry-points", {})


class ToolConfig(PyProjectConfigBase):
    @property
    def support_only_community(self) -> bool:
        return bool(self.get("only-community") or True)

    @property
    def post_version_strategy_override(self) -> str | None:
        post_version_strategy_override = self.get("post_version_strategy_override")
        if os.getenv("WHEEL_POST_VERSION_STRATEGY_OVERRIDE", "None").upper() not in ("FALSE", "NONE"):
            post_version_strategy_override = os.getenv("WHEEL_POST_VERSION_STRATEGY_OVERRIDE")
        return post_version_strategy_override

    @property
    def dependencies_file(self) -> Path | None:
        return self.get("dependencies-file") and Path(self.get("dependencies-file")) or None

    @property
    def odoo_version_override(self) -> str | None:
        return self.get("odoo_version_override") and str(self.get("odoo_version_override")) or None

    @property
    def allow_no_odoo_version(self) -> bool:
        return self.get("allow_no_odoo_version", False)


class PyProjectConfig(PyProjectConfigBase):
    def __init__(self, project_config: dict[str, Any], tool_addon_odoo_wheel: dict[str, Any]) -> None:
        super().__init__(project_config)
        self.addon_odoo_wheel = ToolConfig(tool_addon_odoo_wheel)

    @classmethod
    def from_config(cls, config: dict[str, Any]):
        project_config = config.get("project", {})
        return cls(dict(project_config), dict(config.get("tool", {}).get("addon-odoo-wheel", {})))

    @property
    def name(self) -> str | None:
        return self.get("name")

    @property
    def version(self) -> str | None:
        return self.get("version")

    @property
    def dynamic(self) -> list[str]:
        return self.get("dynamic", [])


def _scm_ls_files(addon_dir: Path) -> list[str]:
    try:
        return subprocess.check_output(["git", "ls-files"], universal_newlines=True, cwd=addon_dir).strip().split("\n")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise NoScmFound() from e


def copy_to(addon_dir: Path, dst: Path, pkg_exclude: Callable[[str, list[str]], list[str]]) -> None:
    if (Path(addon_dir) / "PKG-INFO").exists():
        # if PKG-INFO is present, assume we are in an sdist, copy everything
        shutil.copytree(addon_dir, dst, ignore=pkg_exclude)
        return
    # copy scm controlled files
    try:
        scm_files = _scm_ls_files(addon_dir)
    except NoScmFound:
        # NOTE This requires pip>=21.3 which builds in-tree. Previous pip versions
        # copied to a temporary directory with a different name than the addon, which
        # caused the resulting distribution name to be wrong.
        shutil.copytree(addon_dir, dst, ignore=pkg_exclude)
    else:
        dst.mkdir()
        for f in scm_files:
            d = Path(f).parent
            dstd = dst / d
            if not dstd.is_dir():
                dstd.mkdir(parents=True)
            shutil.copy(addon_dir / f, dstd)


def ensure_absent(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            path.unlink()
