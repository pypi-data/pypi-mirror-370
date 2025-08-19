"""StarUI project configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectConfig:
    """StarUI project configuration."""

    project_root: Path
    css_output: Path
    component_dir: Path

    @property
    def css_output_absolute(self) -> Path:
        return (
            self.project_root / self.css_output
            if not self.css_output.is_absolute()
            else self.css_output
        )

    @property
    def component_dir_absolute(self) -> Path:
        return (
            self.project_root / self.component_dir
            if not self.component_dir.is_absolute()
            else self.component_dir
        )


def detect_css_output(project_root: Path) -> Path:
    """Detect CSS output path based on existing directories."""
    if (project_root / "static").exists():
        return Path("static/css/starui.css")
    elif (project_root / "assets").exists():
        return Path("assets/starui.css")
    return Path("starui.css")


def detect_component_dir(project_root: Path) -> Path:
    """Detect component directory based on existing structure."""
    if (project_root / "components" / "ui").exists():
        return Path("components/ui")
    elif (project_root / "ui").exists():
        return Path("ui")
    return Path("components/ui")


def detect_project_config(project_root: Path | None = None) -> ProjectConfig:
    """Detect project configuration from directory structure."""
    root = project_root or Path.cwd()
    return ProjectConfig(
        project_root=root,
        css_output=detect_css_output(root),
        component_dir=detect_component_dir(root),
    )


def get_content_patterns(project_root: Path) -> list[str]:
    """Get content patterns for Tailwind CSS scanning."""
    return ["**/*.py", "!**/__pycache__/**", "!**/test_*.py"]


def get_project_config(project_root: Path | None = None) -> ProjectConfig:
    """Get project configuration, alias for detect_project_config."""
    return detect_project_config(project_root)
