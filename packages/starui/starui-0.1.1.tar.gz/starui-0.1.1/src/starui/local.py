"""Auto-discover components from local components/ui folder."""

import importlib.util
from pathlib import Path
from typing import Any


def discover_components(base_path: Path | None = None) -> dict[str, Any]:
    """Auto-discover components from components/ui folder."""
    components_path = (base_path or Path.cwd()) / "components" / "ui"

    if not components_path.exists():
        return {}

    components = {}

    for py_file in components_path.glob("*.py"):
        if py_file.name.startswith("_"):
            continue

        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        if not spec or not spec.loader:
            continue

        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                if attr_name[0].isupper() and not attr_name.startswith("_"):
                    attr = getattr(module, attr_name)
                    if callable(attr):
                        components[attr_name] = attr

        except Exception:
            continue

    return components
