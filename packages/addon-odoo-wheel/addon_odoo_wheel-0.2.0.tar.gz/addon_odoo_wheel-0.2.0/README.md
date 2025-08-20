# Addon Odoo Wheel Builder

A standards-compliant Python build backend to package individual Odoo addons.
The main idea and the code is taken from [sbidoul/whool](https://github.com/sbidoul/whool).

## Quick Usage

```toml
[build-system]
requires = ["addon-odoo-wheel"]
build-backend = "addon_odoo_wheel.builder"
```

This config will produce a wheel and the module will be available in the `odoo/addons` namespace.

See complete doc at [addon-odoo-wheel](https://pypi.org/project/addon-odoo-wheel/) to config.

## Well Know Odoo contributors

In src/addon_odoo_wheel/well_know.py you can find the contributors.

To register your company, you only need to add `class` like `class MyCompanyContributor(Contributor):`

```python
class _YourComanyAddonContributor(WellKnowAddonContributor):
  names = ["Author Name"] # Place here all the `author` used in your company

  def get_mail(self, odoo_serie_info:OdooSeries|None) -> str|None:
    # Place here your mail
    return None

  def get_package_prefix(self, odoo_series:OdooSeries|None) -> str:
    # Place here your package prefix by default is `addon-odoo`
```

### TODO

- [ ] Add more option to the `WellKnowAddonContributor` class
- [ ] Use a plugin system `pluggy` to add contributors
- [ ] Improve the documentation
