from pathlib import Path

import typer
from rich.progress import track

from ..config import ProjectConfig, detect_project_config
from ..templates.app_starter import generate_app_starter
from ..templates.css_input import generate_css_input
from .utils import confirm, console, error, info


def validate_project(root: Path, force: bool = False) -> None:
    conflicts: list[str] = []

    if (root / "starui.py").exists():
        conflicts.append("starui.py configuration file")

    for comp_dir in ["components/ui", "ui"]:
        path = root / comp_dir
        if path.exists() and any(path.iterdir()):
            conflicts.append(f"{comp_dir} directory with content")
            break

    if conflicts and not force:
        error_msg = "Project appears to already be initialized. Found:\n"
        error_msg += "\n".join(f"  • {item}" for item in conflicts)
        error(error_msg)
        info("Use --force to reinitialize anyway")
        raise typer.Exit(1)


def setup_directories(config: ProjectConfig, verbose: bool = False) -> None:
    dirs = [
        config.component_dir_absolute,
        config.css_output_absolute.parent,
        config.project_root / "static" / "css",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        if verbose:
            console.print(
                f"[green]Created:[/green] {d.relative_to(config.project_root)}"
            )

    component_init = config.component_dir_absolute / "__init__.py"
    if not component_init.exists():
        component_init.write_text("")
        if verbose:
            console.print(
                f"[green]Created:[/green] {component_init.relative_to(config.project_root)}"
            )


def create_css_input(config: ProjectConfig, verbose: bool = False) -> None:
    input_path = config.project_root / "static" / "css" / "input.css"
    input_path.write_text(generate_css_input(config, include_reset=True))
    if verbose:
        console.print("[green]Created:[/green] input.css")


def create_app(config: ProjectConfig, verbose: bool = False) -> None:
    app_path = config.project_root / "app.py"
    if app_path.exists():
        if verbose:
            console.print("[yellow]Skipped:[/yellow] app.py (already exists)")
        return

    app_path.write_text(
        generate_app_starter(
            config,
            app_name="app.py",
            include_css_link=True,
            include_components_example=True,
        )
    )
    if verbose:
        console.print("[green]Created:[/green] app.py")


def update_gitignore(config: ProjectConfig, verbose: bool = False) -> None:
    gitignore = config.project_root / ".gitignore"

    starui_ignores = [
        "\n# StarUI generated files",
        str(config.css_output),
        "*.css.map",
        "",
        "# StarUI cache",
        ".starui/",
        "",
    ]

    content = gitignore.read_text() if gitignore.exists() else ""

    if "# StarUI generated files" not in content:
        if content and not content.endswith("\n"):
            content += "\n"
        gitignore.write_text(content + "\n".join(starui_ignores))
        if verbose:
            action = "Updated" if content else "Created"
            console.print(f"[green]{action}:[/green] .gitignore")
    elif verbose:
        console.print("[yellow]Skipped:[/yellow] .gitignore (StarUI patterns exist)")


def create_config_file(config: ProjectConfig, verbose: bool = False) -> None:
    config_path = config.project_root / "starui.py"

    if config_path.exists():
        if verbose:
            console.print("[yellow]Skipped:[/yellow] starui.py (already exists)")
        return

    template = f'''"""StarUI configuration."""

from pathlib import Path

CSS_OUTPUT = Path("{config.css_output}")
COMPONENT_DIR = Path("{config.component_dir}")
'''

    config_path.write_text(template)
    if verbose:
        console.print("[green]Created:[/green] starui.py")


def init_command(
    force: bool = typer.Option(False, "--force", help="Force initialization"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show details"),
    config: bool = typer.Option(False, "--config", help="Create starui.py"),
) -> None:
    """Initialize a new StarUI project."""

    try:
        root = Path.cwd()

        if verbose:
            console.print(f"[blue]Initializing StarUI in:[/blue] {root}")

        project_config = detect_project_config(root)

        if verbose:
            console.print(f"[dim]CSS output:[/dim] {project_config.css_output}")
            console.print(f"[dim]Components:[/dim] {project_config.component_dir}")

        validate_project(root, force)

        # Confirm if overwriting
        if not force:
            overwrites: list[str] = []
            if project_config.css_output_absolute.exists():
                overwrites.append(str(project_config.css_output))

            if overwrites:
                console.print("\n[yellow]Will overwrite:[/yellow]")
                for f in overwrites:
                    console.print(f"  • {f}")

                if not confirm("\nProceed?", default=True):
                    info("Cancelled")
                    raise typer.Exit()

        # Initialize
        console.print("\n[green]✨ Initializing StarUI...[/green]")

        steps = [
            (
                "Creating directories",
                lambda: setup_directories(project_config, verbose),
            ),
            ("Creating CSS input", lambda: create_css_input(project_config, verbose)),
            ("Creating starter app", lambda: create_app(project_config, verbose)),
            ("Updating .gitignore", lambda: update_gitignore(project_config, verbose)),
        ]

        if config:
            steps.append(
                ("Creating config", lambda: create_config_file(project_config, verbose))
            )

        if verbose:
            for name, func in steps:
                console.print(f"[blue]{name}...[/blue]")
                func()
        else:
            for _, func in track(steps, description="Initializing..."):
                func()

        # Success
        console.print("\n[green]🎉 StarUI initialized![/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Run [blue]star dev[/blue] to start development")
        console.print("  2. Run [blue]star add button[/blue] to add components")
        console.print("  3. Run [blue]star build[/blue] for production CSS")

        if not config:
            console.print(
                "\n[dim]💡 Use [blue]star init --config[/blue] for config file[/dim]"
            )

    except Exception as e:
        error(f"Initialization failed: {e}")
        raise typer.Exit(1) from e
