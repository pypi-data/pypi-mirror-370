import sys

__all__ = ["importlib_metadata", "tomllib", "long_description", "make_classifiers"]

if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    import importlib.metadata as importlib_metadata

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def long_description(addon):
    from manifestoo_core.metadata import _long_description as manifestoo_long_description

    return manifestoo_long_description(addon)


def make_classifiers(odoo_series, manifest):
    from manifestoo_core.metadata import _make_classifiers as manifestoo_make_classifiers

    return manifestoo_make_classifiers(odoo_series, manifest)
