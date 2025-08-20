import re

import typer

from starui.config import get_project_config
from starui.registry.loader import ComponentLoader

from .utils import confirm, console, error, info, status_context, success, warning


def add_command(
    components: list[str] = typer.Argument(..., help="Components to add"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show details"),
) -> None:
    """Add components to your project."""

    invalid = [c for c in components if not re.match(r"^[a-z][a-z0-9-]*$", c)]
    if invalid:
        error(f"Invalid component names: {', '.join(invalid)}")
        raise typer.Exit(1)

    try:
        config = get_project_config()
        loader = ComponentLoader()
    except Exception as e:
        error(f"Initialization failed: {e}")
        raise typer.Exit(1) from e

    with status_context("Installing components..."):
        try:
            all_components = {}
            for component in components:
                if verbose:
                    info(f"Resolving {component}...")
                all_components.update(
                    loader.load_component_with_dependencies(component)
                )

            component_dir = config.component_dir_absolute
            conflicts = [
                component_dir / f"{name}.py"
                for name in all_components
                if (component_dir / f"{name}.py").exists()
            ]

            if conflicts and not force:
                warning(f"Found {len(conflicts)} existing files:")
                for path in conflicts:
                    console.print(f"  • {path}")
                if not confirm("Overwrite?", default=False):
                    raise typer.Exit(0)

            component_dir.mkdir(parents=True, exist_ok=True)
            (component_dir / "__init__.py").touch()

            for name, source in all_components.items():
                source = re.sub(r"from\s+fasthtml\.", "from starhtml.", source)
                source = re.sub(r"import\s+fasthtml\.", "import starhtml.", source)
                source = re.sub(
                    r"from\s+\.utils\s+import", "from starui import", source
                )

                (component_dir / f"{name}.py").write_text(source)

            success(f"Installed: {', '.join(all_components.keys())}")

            if verbose:
                info(f"Location: {component_dir}")

            console.print("\n💡 Next steps:")
            console.print(
                f"  • Import: from starui import {list(all_components)[0].title().replace('_', '')}"
            )

        except Exception as e:
            error(f"Installation failed: {e}")
            raise typer.Exit(1) from e
