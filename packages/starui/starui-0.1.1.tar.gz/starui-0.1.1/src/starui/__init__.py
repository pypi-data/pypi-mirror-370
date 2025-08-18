"""Python-first UI component library for StarHTML applications."""

__version__ = "0.1.0"

from .local import discover_components
from .registry.components.utils import cn, component_classes, cva

_components = discover_components()
globals().update(_components)

__all__ = [
    "__version__",
    "cn",
    "cva",
    "component_classes",
    *list(_components.keys()),  # pyright: ignore[reportUnsupportedDunderAll]
]


def __getattr__(name: str):
    if name in _components:
        return _components[name]

    components = discover_components()
    if name in components:
        _components[name] = components[name]
        return components[name]

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
