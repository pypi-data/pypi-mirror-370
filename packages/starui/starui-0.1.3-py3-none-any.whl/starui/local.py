"""Component discovery for local UI modules."""

import importlib.util
from pathlib import Path
from typing import Any


def discover_components(base_path: Path | None = None) -> dict[str, Any]:
    """Discover components from components/ui folder."""
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

            components.update(
                {
                    name: attr
                    for name in dir(module)
                    if name[0].isupper() and callable(attr := getattr(module, name))
                }
            )
        except Exception:
            continue

    return components
