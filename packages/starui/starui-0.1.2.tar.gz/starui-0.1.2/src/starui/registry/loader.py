"""Component loader and dependency resolver."""

from .client import RegistryClient


class ComponentLoader:
    """High-level component loader with dependency resolution."""

    def __init__(self, client: RegistryClient | None = None) -> None:
        self.client = client or RegistryClient()
        self.resolver = DependencyResolver(self.client)

    def load_component(self, component_name: str) -> str:
        """Load a single component's source code."""
        if not self.client.component_exists(component_name):
            raise FileNotFoundError(
                f"Component '{component_name}' not found in registry"
            )
        return self.client.get_component_source(component_name)

    def load_component_with_dependencies(self, component_name: str) -> dict[str, str]:
        """Load a component and all its dependencies."""
        resolved_order = self.resolver.resolve_dependencies(component_name)

        component_sources: dict[str, str] = {}
        for comp_name in resolved_order:
            if not self.client.component_exists(comp_name):
                raise FileNotFoundError(f"Dependency '{comp_name}' not found")
            component_sources[comp_name] = self.client.get_component_source(comp_name)

        return component_sources


class DependencyResolver:
    """Resolves component dependencies with circular dependency detection."""

    def __init__(self, client: RegistryClient) -> None:
        self.client = client

    def resolve_dependencies(self, component_name: str) -> list[str]:
        """Resolve all dependencies for a component in topological order."""
        resolved: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(comp_name: str) -> None:
            if comp_name in visiting:
                raise ValueError(
                    f"Circular dependency detected involving '{comp_name}'"
                )
            if comp_name in visited:
                return

            try:
                metadata = self.client.get_component_metadata(comp_name)
            except FileNotFoundError:
                raise FileNotFoundError(f"Component '{comp_name}' not found") from None

            visiting.add(comp_name)

            for dependency in metadata["dependencies"]:
                visit(dependency)

            visiting.remove(comp_name)
            visited.add(comp_name)

            if comp_name not in resolved:
                resolved.append(comp_name)

        visit(component_name)
        return resolved
