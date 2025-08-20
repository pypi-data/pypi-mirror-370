from __future__ import annotations

import email
import logging
import re
from email.message import Message
from email.utils import formataddr
from pathlib import Path

from manifestoo_core.addon import Addon
from manifestoo_core.exceptions import UnsupportedManifestVersion
from manifestoo_core.manifest import Manifest
from manifestoo_core.metadata import OdooSeriesInfo
from manifestoo_core.odoo_series import MIN_VERSION_PARTS, OdooSeries
from packaging.requirements import Requirement

from . import compat
from .contributors_api import ContributorABC, ContributorFactory
from .utils import (
    EXTRA_NAME_RE,
    WHEEL_TAG,
    PyProjectConfig,
    load_pyproject_toml,
    normalize_label,
    odoo_licence_to_SDPX,
)

_logger = logging.getLogger(__name__)

MANIFEST_VERSION_REGEX = re.compile(
    r"^((?P<odoo_version>1[2-8]\.[0-1])\.)?(?P<major>0|[1-9]\d*)(\.(?P<minor>0|[1-9]\d*))?(\.(?P<patch>0|[1-9]\d*))?$"
)


class AddonMetadata:
    addon: Addon
    odoo_series: OdooSeries | None
    odoo_series_info: OdooSeriesInfo | None
    """The Odoo version found from the module version or the key `odoo_version_override` in pyproject.toml"""
    git_postversion: str

    @classmethod
    def from_addon_dir(
        cls, addon_dir: Path, allow_not_installable: bool = True, force_addon_name: str = None
    ) -> "AddonMetadata":
        _addon = Addon.from_addon_dir(addon_dir, allow_not_installable)
        if force_addon_name:
            _addon.name = force_addon_name
        pyproject_options = load_pyproject_toml(addon_dir)
        return cls(pyproject_options, _addon)

    def __init__(self, pyproject_options: PyProjectConfig, addon: Addon) -> None:
        self.addon = addon
        self.pyproject_options = pyproject_options
        self.odoo_series = self._get_odoo_series()
        self.git_postversion = (
            self.pyproject_options.addon_odoo_wheel.post_version_strategy_override
            or self.module_contributor.git_postversion_strategy(self.odoo_series)
        )

    @property
    def python_addon_path(self) -> str:
        return f"odoo.addons.{self.addon.name}"

    @property
    def module_contributor(self) -> ContributorABC:
        return ContributorFactory.from_author(self.manifest.author)

    @property
    def metadata(self) -> Message:
        """The metadata extracted from manifest"""
        return self.generate_metadata()

    @property
    def addon_path(self):
        return self.addon.path

    @property
    def odoo_series_info(self) -> OdooSeriesInfo | None:
        return self.odoo_series and OdooSeriesInfo.from_odoo_series(self.odoo_series)

    @property
    def wheel_name(self) -> str:
        return f"{self.sdist_name}-{WHEEL_TAG}"

    @property
    def sdist_name(self) -> str:
        return "{}-{}".format(self.metadata["Name"].replace("-", "_").replace(".", "_"), self.metadata["Version"])

    @property
    def addon_name(self):
        return self.addon.name

    @property
    def manifest(self) -> Manifest:
        return self.addon.manifest

    def _get_odoo_series(self) -> OdooSeries | None:
        if self.pyproject_options.addon_odoo_wheel.odoo_version_override:
            return OdooSeries.from_str(self.pyproject_options.addon_odoo_wheel.odoo_version_override)
        _version_pyproject = self.pyproject_options.version
        _version_manifest = self.addon.manifest.version
        if not _version_pyproject and not _version_manifest:
            raise ValueError("Manifest version or pyproject.toml version must be set")
        if _version_pyproject and _version_manifest and _version_pyproject != _version_manifest:
            msg = (
                "Manifest version or pyproject.toml version must be the same, "
                "or set version in pyproject.toml to dynamic"
            )
            raise ValueError(msg)
        _version = _version_manifest or _version_pyproject
        matchs = MANIFEST_VERSION_REGEX.match(_version)
        if not matchs:
            msg = "Version in manifest or in your pyproject.toml must follow semver convention:"
            raise UnsupportedManifestVersion(msg)
        odoo_version = matchs.group("odoo_version")
        if odoo_version:
            return OdooSeries.from_str(odoo_version)
        return None

    def generate_metadata(self) -> Message:
        """Return Python Package Metadata 2.1 for an Odoo addon directory as an
        ``email.message.Message``.

        The Description field is absent and is stored in the message payload. All values are
        guaranteed to not contain newline characters, except for the payload.

        ``precomputed_metadata_path`` may point to a file containing pre-computed metadata
        that will be used to obtain the Name and Version, instead of looking at the addon
        directory name or manifest version + VCS, respectively. This is useful to process a
        manifest from a sdist tarball with PKG-INFO, for example, when the original
        directory name or VCS is not available to compute the package name and version.

        This function may raise :class:`manifestoo_core.exceptions.ManifestooException` if
        ``addon_dir`` does not contain a valid installable Odoo addon for a supported Odoo
        version.
        """
        if (self.addon.path / "PKG-INFO").exists():
            # if PKG-INFO is present, assume we are in an sdist, copy everything
            with (self.addon.path / "PKG-INFO").open("r") as f:
                return email.parser.HeaderParser().parse(f)
        return self.construct_metadata_file_2_4()

    def construct_metadata_file_2_4(self) -> Message:
        """
        https://peps.python.org/pep-0639/
        """
        msg = Message()

        msg["Metadata-Version"] = "2.4"
        self._set_name(msg)
        self._set_version(msg)
        self._set_urls(msg)
        self._set_authors(msg)
        self._set_license(msg)
        self._set_classifier(msg)
        self._set_require_python(msg)
        self._set_dependencies(msg)
        self._set_extra_dependencies(msg)
        self._set_description(msg)
        return msg

    def _set_name(self, msg: Message):
        if self.pyproject_options and not self.pyproject_options.name:
            raise ValueError("The `project.name` field must be set in pyproject.toml")

        pkg_name = self.pyproject_options.name
        if not pkg_name:
            prefix = self.pyproject_options.addon_odoo_wheel.get("package_prefix")
            if not prefix:
                prefix = self.module_contributor.get_package_prefix(self.odoo_series)
            pkg_name = f"{prefix}-{self.addon_name}"

        msg["Name"] = pkg_name

    def _set_version(self, msg: Message):
        _version = self.manifest.version
        if "version" not in self.pyproject_options.dynamic and self.pyproject_options.version:
            if _version != self.pyproject_options.version:
                raise ValueError("Version must be same between pyproject.toml and __manifest__.py")
            _logger.debug("Force set version from pyproject.toml: %s -> %s", _version, self.pyproject_options.version)
            msg["Version"] = self.pyproject_options.version
            return

        _logger.debug("Manifest version: %s", _version)
        _logger.debug("Odoo version: %s", self.odoo_series and self.odoo_series.value or "undefined")
        _logger.debug("version: %s", _version)
        matches = MANIFEST_VERSION_REGEX.match(_version)
        if not matches:
            msg = f"Can't match version '{_version}', see regex https://regex101.com/r/HjHXm7/1"
            raise UnsupportedManifestVersion(msg)

        odoo_version = matches.group("odoo_version") or None
        pkg_major = matches.group("major") or "1"
        pkg_minor = matches.group("minor") or "0"
        pkg_patch = matches.group("patch") or "0"
        if not odoo_version and not self.odoo_series and self.pyproject_options.addon_odoo_wheel.allow_no_odoo_version:
            msg["Version"] = _version
            return
        if not odoo_version and self.odoo_series.value == ".".join((pkg_major, pkg_minor)):
            _logger.debug("Manifest version is same as Odoo version. Force set to 1.0.0")
            odoo_version = ".".join((pkg_major, pkg_minor))
            pkg_major = "1"
            pkg_minor = "0"
            pkg_patch = "0"

        if odoo_version and self.odoo_series:
            if odoo_version != self.odoo_series:
                msg = f"The version in __manifest__.py start with {odoo_version} but {self.odoo_series.value} is found"
                raise UnsupportedManifestVersion(msg)
        if not odoo_version and self.odoo_series:
            _logger.debug(
                "Force set odoo version before module version from odoo_version_override: %s.%s",
                self.odoo_series.value,
                _version,
            )
            odoo_version = self.odoo_series.value

        _logger.debug(matches)
        normal_version = ".".join(
            tuple(
                filter(
                    bool,
                    (
                        odoo_version,
                        pkg_major,
                        pkg_minor,
                        pkg_patch,
                    ),
                )
            )
        )
        matches: re.Match = MANIFEST_VERSION_REGEX.match(normal_version)
        if not matches:
            msg = f"Can't match version '{normal_version}', see regex https://regex101.com/r/HjHXm7/1"
            raise UnsupportedManifestVersion(msg)
        msg["Version"] = normal_version
        _logger.debug("Normalized version -> %s", normal_version)

    def _set_description(self, msg: Message):
        if self.pyproject_options.get("summary"):
            msg["Summary"] = self.pyproject_options.get("summary").splitlines()[0]
        to_try = [("README.md", "text/markdown"), ("README.rst", "text/x-rst")]
        if self.pyproject_options.get("readme"):
            content_type = "text/plain"
            if Path(self.pyproject_options.get("readme")).suffix == ".md":
                content_type = "text/markdown"
            if Path(self.pyproject_options.get("readme")).suffix == ".rst":
                content_type = "text/x-rst"
            to_try.insert(0, (self.pyproject_options.get("readme"), content_type))

        for read_to_try in to_try:
            if not read_to_try[0]:
                continue
            readme_path = self.addon.path / read_to_try[0]
            if readme_path.exists() and readme_path.is_file():
                msg["Description-Content-Type"] = read_to_try[1]
                msg.set_payload(readme_path.read_text(encoding="utf-8"))
                break
        else:
            if self.manifest.description:
                msg["Description-Content-Type"] = "text/plain"
                msg["Description"] = self.manifest.description

    def _set_dependencies(self, msg: Message):
        dependencies = []
        source = {
            "project.dependencies" if self.pyproject_options.dependencies else None,
            "addon_odoo_wheel.dependencies" if self.pyproject_options.addon_odoo_wheel.dependencies else None,
            "addon_odoo_wheel.dependencies_file" if self.pyproject_options.addon_odoo_wheel.dependencies_file else None,
        }
        source.remove(None)
        if len(source) > 1:
            msg = "Only one source of 'dependencies' can be set. Found: " + ", ".join(source)
            raise ValueError(msg)
        if len(source) == 0 and (self.addon.path / "requirements.txt").exists():
            _logger.debug("Using 'requirements.txt' inside %s for dependencies", self.addon.path)
            self.pyproject_options.addon_odoo_wheel["dependencies-file"] = self.addon.path / "requirements.txt"

        if self.pyproject_options.dependencies:
            dependencies = self.pyproject_options.dependencies
        if self.pyproject_options.addon_odoo_wheel.dependencies:
            dependencies = self.pyproject_options.addon_odoo_wheel.dependencies
        if self.pyproject_options.addon_odoo_wheel.dependencies_file:
            with self.pyproject_options.addon_odoo_wheel.dependencies_file.open("r") as f:
                dependencies = [Requirement(dep) for dep in f.read().splitlines() if not dep.startswith("#")]

        for dependency in dependencies:
            msg["Requires-Dist"] = str(dependency)

    def _set_extra_dependencies(self, msg: Message):
        extras = self.pyproject_options.get("optional-dependencies") or self.pyproject_options.addon_odoo_wheel.get(
            "optional-dependencies"
        )
        if not extras:
            return

        for extra, dependencies in extras.items():
            if not EXTRA_NAME_RE.match(extra):
                raise ValueError(
                    f"Invalid extra name: {extra!r} See: https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use"
                )
            msg["Provides-Extra"] = extra
            for dependency in dependencies:
                msg["Requires-Dist"] = f"{dependency}; extra == {extra!r}"

    def _set_require_python(self, msg: Message):
        requires_python = (
            self.pyproject_options.requires_python
            or (self.odoo_series and self.odoo_series_info.python_requires)
            or self.pyproject_options.addon_odoo_wheel.requires_python
        )
        if requires_python:
            msg["Requires-Python"] = requires_python

    def _set_classifier(self, msg: Message):
        classifiers = set(self.pyproject_options.classifiers)
        if not self.pyproject_options:
            classifiers |= set(self.pyproject_options.addon_odoo_wheel.classifiers)
        classifiers |= set(self.module_contributor.get_classifiers(self.odoo_series))
        _, classifier_license = odoo_licence_to_SDPX.get(self.manifest.license, (None, None))
        if classifier_license:
            classifiers.add(classifier_license)
        if self.odoo_series:
            _manifest_copy = Manifest.from_dict(self.manifest.manifest_dict)
            if not self.manifest.development_status:
                version_parts = self.manifest.version.split(".")
                if len(version_parts) == MIN_VERSION_PARTS:
                    version_parts = version_parts[2:]
                development_status = "stable" if int(version_parts[0]) > 0 else "alpha"
                _manifest_copy = Manifest.from_dict(
                    dict(self.manifest.manifest_dict, development_status=development_status)
                )
            classifiers |= set(compat.make_classifiers(self.odoo_series, _manifest_copy))
        for classifier in sorted(list(classifiers)):
            msg["Classifier"] = classifier

    def _set_license(self, msg: Message):
        license_map, _ = odoo_licence_to_SDPX.get(self.manifest.license, (None, None))
        if self.addon.manifest.license == "Other proprietary" and not self.pyproject_options.get("license"):
            raise ValueError("field `project.license` must be static when using 'Other proprietary' value in manifest")
        msg["License-Expression"] = license_map or self.pyproject_options.get("license") or "AGPL-3.0-or-later"
        for license_file in self.pyproject_options.get("license_files") or []:
            msg["License-File"] = license_file

    def _set_urls(self, msg: Message):
        urls = self.pyproject_options.get("urls", {})
        urls["Homepage"] = self.manifest.website
        for label, url in urls.items():
            is_well_know, label_n = normalize_label(label)
            msg["Project-URL"] = f"{label_n}, {url}"

    def _set_authors(self, msg: Message):
        odoo_authors = []
        if self.manifest.author:
            odoo_authors = self.manifest.author.split(",")
        author_values = []
        author_no_mail = []
        for author in self.pyproject_options.get("authors", []):
            if author["name"] in odoo_authors:
                odoo_authors.remove(author["name"])
            author_values.append(formataddr((author["name"], author["email"])))

        for odoo_author in odoo_authors:
            email = self.module_contributor.get_mail(self.odoo_series)
            if email:
                author_values.append(formataddr((odoo_author, email)))
            else:
                author_no_mail.append(odoo_author)
        if author_values:
            msg["Author-Email"] = ", ".join(author_values)
        if author_no_mail:
            msg["Author"] = ", ".join(author_no_mail)


def _no_nl(s: str | None) -> str | None:
    if not s:
        return s
    return " ".join(s.split())
