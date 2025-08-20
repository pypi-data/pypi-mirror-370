from pathlib import Path

import pytest
from manifestoo_core.addon import Addon
from manifestoo_core.exceptions import UnsupportedManifestVersion
from manifestoo_core.manifest import Manifest
from manifestoo_core.odoo_series import OdooSeries
from packaging.requirements import Requirement

from addon_odoo_wheel import metadata
from addon_odoo_wheel.utils import PyProjectConfig


def test_dynamic_version(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "project": {
                    "name": "company-addon-name",
                    "dynamic": ["version"],
                }
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="18.0.1.2.3",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.metadata["Version"] == addon_metadata.addon.manifest.version == "18.0.1.2.3"
    assert addon_metadata.odoo_series == OdooSeries.v18_0
    assert addon_metadata.metadata["Name"] == "company-addon-name"
    assert addon_metadata.wheel_name == "company_addon_name-18.0.1.2.3-py3-none-any"
    assert addon_metadata.sdist_name == "company_addon_name-18.0.1.2.3"
    assert not addon_metadata.metadata["Requires-Dist"]


def test_not_same_version(module_data: Path):
    with pytest.raises(ValueError) as excinfo:
        metadata.AddonMetadata(
            PyProjectConfig.from_config(
                {
                    "project": {
                        "name": "company-addon-name",
                        "version": "2.3.4",
                    }
                }
            ),
            Addon(
                name="addon_name",
                manifest=Manifest.from_dict(
                    dict(
                        version="18.0.1.2.3",
                        depends=["base"],
                        installable=True,
                    )
                ),
                manifest_path=module_data,
            ),
        )
    assert excinfo.value.args[0] == (
        "Manifest version or pyproject.toml version must be the same, or set version in pyproject.toml to dynamic"
    )


def test_fixed_version(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "project": {
                    "name": "company-addon-name",
                    "version": "18.0.1.2.3",
                }
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="18.0.1.2.3",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.addon.manifest.version == addon_metadata.metadata["Version"] == "18.0.1.2.3"
    assert addon_metadata.odoo_series == OdooSeries.v18_0
    assert addon_metadata.metadata["Name"] == "company-addon-name"
    assert addon_metadata.wheel_name == "company_addon_name-18.0.1.2.3-py3-none-any"
    assert addon_metadata.sdist_name == "company_addon_name-18.0.1.2.3"
    assert not addon_metadata.metadata["Requires-Dist"]


def test_depends_manifest(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "project": {
                    "name": "company-addon-name",
                    "dynamic": ["version"],
                    "dependencies": ["odoo-addon-web-environment-ribbon>=18.0"],
                },
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="18.0.1.2.3",
                    depends=["base", "purchase", "web_environment_ribbon"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.odoo_series == OdooSeries.v18_0
    assert addon_metadata.metadata["Requires-Dist"] == str(Requirement("odoo-addon-web-environment-ribbon>=18.0"))


def test_force_odoo_series_version(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "project": {
                    "name": "company-addon-name",
                },
                "tool": {"addon-odoo-wheel": {"odoo_version_override": "18.0"}},
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="1.2.3",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.addon.manifest.version == "1.2.3"
    assert addon_metadata.metadata["Version"] == "18.0.1.2.3"
    assert addon_metadata.odoo_series == OdooSeries.v18_0
    assert addon_metadata.metadata["Name"] == "company-addon-name"
    assert addon_metadata.wheel_name == "company_addon_name-18.0.1.2.3-py3-none-any"
    assert addon_metadata.sdist_name == "company_addon_name-18.0.1.2.3"
    assert not addon_metadata.metadata["Requires-Dist"]


def test_auto_config_1(module_data: Path):
    """
    Test auto defining name off the wheel from the name of the odoo module.
    The version is defined from the manifest too.
    """
    module1_path = module_data / "module_with_version"

    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config({}),
        Addon(
            name="my_odoo_addon",
            manifest=Manifest.from_dict(
                dict(
                    version="18.0.1.2.3",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module1_path,
        ),
    )
    assert addon_metadata.addon.name == "my_odoo_addon"
    assert addon_metadata.metadata["Version"] == addon_metadata.addon.manifest.version == "18.0.1.2.3"
    assert addon_metadata.odoo_series == OdooSeries.v18_0
    assert addon_metadata.wheel_name == "addon_odoo_my_odoo_addon-18.0.1.2.3-py3-none-any"
    assert addon_metadata.sdist_name == "addon_odoo_my_odoo_addon-18.0.1.2.3"
    assert not addon_metadata.metadata["Requires-Dist"]


def test_force_semver_1(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "tool": {"addon-odoo-wheel": {"odoo_version_override": "18.0"}},
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="18.0",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.addon.manifest.version == "18.0"
    assert addon_metadata.metadata["Version"] == "18.0.1.0.0"


def test_force_semver_2(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "tool": {"addon-odoo-wheel": {"odoo_version_override": "18.0"}},
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="2",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.addon.manifest.version == "2"
    assert addon_metadata.metadata["Version"] == "18.0.2.0.0"


def test_force_semver_3(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "tool": {"addon-odoo-wheel": {"odoo_version_override": "18.0"}},
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="2.1",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.addon.manifest.version == "2.1"
    assert addon_metadata.metadata["Version"] == "18.0.2.1.0"


def test_force_semver_4(module_data: Path):
    addon_metadata = metadata.AddonMetadata(
        PyProjectConfig.from_config(
            {
                "tool": {"addon-odoo-wheel": {"odoo_version_override": "18.0"}},
            }
        ),
        Addon(
            name="addon_name",
            manifest=Manifest.from_dict(
                dict(
                    version="2.1.3",
                    depends=["base"],
                    installable=True,
                )
            ),
            manifest_path=module_data,
        ),
    )
    assert addon_metadata.addon.name == "addon_name"
    assert addon_metadata.addon.manifest.version == "2.1.3"
    assert addon_metadata.metadata["Version"] == "18.0.2.1.3"


def test_force_semver_5(module_data: Path):
    with pytest.raises(UnsupportedManifestVersion) as excinfo:
        metadata.AddonMetadata(
            PyProjectConfig.from_config(
                {
                    "tool": {"addon-odoo-wheel": {"odoo_version_override": "18.0"}},
                }
            ),
            Addon(
                name="addon_name",
                manifest=Manifest.from_dict(
                    dict(
                        version="16.0.2.1.3",
                        depends=["base"],
                        installable=True,
                    )
                ),
                manifest_path=module_data,
            ),
        ).generate_metadata()
    assert excinfo.value.args[0] == ("The version in __manifest__.py start with 16.0 but 18.0 is found")
