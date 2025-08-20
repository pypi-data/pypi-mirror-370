import os
from pathlib import Path

from manifestoo_core.addons_set import AddonsSet


def main() -> None:
    addon_set = AddonsSet()
    for path in os.listdir(str(Path.cwd())):
        addon_set.add_from_addons_dir(Path(path))

    for addon_name, addon in addon_set.items():
        print(f"=== {addon_name} ===")
        print(f"  - version: {addon.manifest.version}")
        print(f"  - description: {addon.manifest.description}")
        print("Build Source distribution")


if __name__ == "__main__":
    main()
