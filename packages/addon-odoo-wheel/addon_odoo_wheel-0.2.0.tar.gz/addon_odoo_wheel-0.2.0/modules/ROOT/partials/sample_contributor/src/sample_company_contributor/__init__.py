from __future__ import annotations
from addon_odoo_wheel.contributors_api import ContributorABC, OdooSeries


class SampleCompanyContributor(ContributorABC):
    names = ["SAMPLE_COMPANY"]  # <.>

    def get_mail(self, odoo_series: OdooSeries | None) -> str:
        return f"odoo+{odoo_series and odoo_series.value or 'any'}@sample_company.com"  # <.>

    def odoo_series_required(self) -> bool:
        return True  # <.>

    def get_package_prefix(self, odoo_series: OdooSeries | None) -> str | None:
        return "sample-company-addon"  # <.>

    def git_postversion_strategy(self, odoo_series: OdooSeries | None) -> str:
        return super().git_postversion_strategy(odoo_series)  # <.>

    def get_classifiers(self, odoo_series: OdooSeries | None) -> list[str]:  # <.>
        return super().get_classifiers(odoo_series) + [
            "Private :: Do Not Upload",
        ]
