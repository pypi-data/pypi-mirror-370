import importlib
import pkgutil
from types import (
    ModuleType,
)


def import_submodules(package: str, module_name: str) -> list[ModuleType]:
    """Импортирует подмодули пакета."""
    package = importlib.import_module(package)
    modules = []

    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if is_pkg:
            full_name = f'{package.__name__}.{name}'
            try:
                modules.append(importlib.import_module(module_name, full_name))
            except ModuleNotFoundError:
                continue

    return modules
