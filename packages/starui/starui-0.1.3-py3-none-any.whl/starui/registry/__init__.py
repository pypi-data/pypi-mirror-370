"""StarUI component registry system."""

from .client import RegistryClient
from .loader import ComponentLoader, DependencyResolver

__all__ = [
    "RegistryClient",
    "ComponentLoader",
    "DependencyResolver",
]
