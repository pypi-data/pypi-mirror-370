from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from importlib_metadata import entry_points
from manifestoo_core.git_postversion import POST_VERSION_STRATEGY_DOT_N
from manifestoo_core.metadata import OdooSeriesInfo
from manifestoo_core.odoo_series import OdooSeries

__all__ = ["ContributorABC", "OdooSeries"]


class ContributorABC(ABC):
    names = []

    @abstractmethod
    def get_mail(self, odoo_series: OdooSeries | None) -> str | None:
        """
        Allow you to define an email based on the odoo series if you want.
        The odoo series is passed as a parameter only if it can be defined. See the documentation.
        :param odoo_series: Allow to change the mail depending of the version if you want
        :return: A mail or None if you don't want to define an email
        """

    def odoo_series_required(self) -> bool:
        """
        Allow to tell if you want to build an addon if the version of Odoo can't be defined.
        :return: True, mean the build will failed if the odoo series can't be defined
        """
        return False

    @abstractmethod
    def get_package_prefix(self, odoo_series: OdooSeries | None) -> str | None:
        """
        The prefix of the wheel name.
        The final wheel name will be the following: <prefix>-<addon_name>.whl
        :param odoo_series: Allow to change the name depending of the version if you want
        :return: The prefix, if none is returned, only the addon name will be used
        """

    def git_postversion_strategy(self, odoo_series: OdooSeries | None) -> str:
        if odoo_series:
            return OdooSeriesInfo.from_odoo_series(odoo_series).git_postversion_strategy
        return POST_VERSION_STRATEGY_DOT_N

    def get_classifiers(self, odoo_series: OdooSeries | None) -> list[str]:
        """
        Allow to add classifiers to the metadata
        See https://pypi.org/classifiers/ to search for available classifiers
        :param odoo_series: Allow to change the classifiers depending of the version if you want
        :return:
        """
        default = [
            "Programming Language :: Python",
            "Framework :: Odoo",
        ]
        if odoo_series:
            default.append(f"Framework :: Odoo :: {odoo_series.value}")
        return default

    def pkg_exclude(self, dist: str) -> Callable[[str, list[str]], list[str]]:
        def _callback_ignore(src, names):
            if Path(src).name == "static":
                return ["description"]
            return []

        return _callback_ignore


class ContributorFactory:
    names = []
    _registry_well_know: dict[str | None, ContributorABC] = {}

    @classmethod
    def _load_plugins(cls):
        if cls._registry_well_know:
            return
        odoo_addon_contributor = entry_points(group="odoo-addon-contributor")
        for ep in odoo_addon_contributor:
            klass = ep.load()
            for name in klass.names:
                if name in cls._registry_well_know:
                    raise ValueError(f"Addon contributor {name} already registered")
                cls._registry_well_know[name and name.upper()] = klass()
        print(odoo_addon_contributor, cls._registry_well_know.keys())

    @classmethod
    def from_author(cls, name: str | None) -> ContributorABC:
        cls._load_plugins()
        return cls._registry_well_know.get(name and name.upper() or None) or _UnknownAddonContributor()


class _UnknownAddonContributor(ContributorABC):
    names = [None, ""]

    def get_mail(self, odoo_serie_info: OdooSeries | None) -> str | None:
        return None

    def get_package_prefix(self, odoo_series: OdooSeries | None) -> str:
        return "addon-odoo"
