from __future__ import annotations

from typing import Callable

from manifestoo_core.metadata import OdooSeriesInfo
from manifestoo_core.odoo_series import OdooSeries

from .contributors_api import ContributorABC


class OcaContributor(ContributorABC):
    names = ["OCA", "Odoo Community Association (OCA)"]

    def get_mail(self, odoo_serie_info: OdooSeries | None) -> str:
        return "support@odoo-community.org"

    def get_package_prefix(self, odoo_series: OdooSeries | None) -> str:
        return odoo_series and OdooSeriesInfo.from_odoo_series(odoo_series).pkg_name_pfx or "odoo-addon"


class MangonoContributor(ContributorABC):
    names = ["Mangono", "NDP Systemes"]

    def get_mail(self, odoo_serie: OdooSeries | None) -> str:
        return "opensource+odoo@mangono.fr"

    def get_package_prefix(self, odoo_serie: OdooSeries | None) -> str:
        return "mangono-addon"


class OdooContributor(ContributorABC):
    names = ["Odoo", "Odoo SA"]

    def get_mail(self, odoo_serie: OdooSeries | None) -> str:
        return "support@odoo.com"

    def get_package_prefix(self, odoo_serie: OdooSeries | None) -> str:
        return "odoo-addon-official"

    def pkg_exclude(self, dist: str) -> Callable[[str, list[str]], list[str]]:
        return lambda src, names: []
