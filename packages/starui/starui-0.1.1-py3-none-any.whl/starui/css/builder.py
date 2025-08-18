"""CSS build pipeline with Tailwind integration."""

import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ..config import ProjectConfig, get_content_patterns
from ..templates.css_input import generate_css_input
from .binary import TailwindBinaryManager


class BuildMode(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class BuildError(Exception):
    pass


@dataclass
class BuildResult:
    success: bool
    css_path: Path | None = None
    build_time: float | None = None
    classes_found: int | None = None
    css_size_bytes: int | None = None
    error_message: str | None = None


def extract_classes(content: str) -> set[str]:
    """Extract CSS classes from content."""
    classes: set[str] = set()

    # Attribute patterns
    for pattern in [
        r'cls\s*=\s*["\']([^"\']*)["\']',
        r'class_\s*=\s*["\']([^"\']*)["\']',
        r'className\s*=\s*["\']([^"\']*)["\']',
    ]:
        for match in re.findall(pattern, content, re.MULTILINE):
            classes.update(match.split())

    # cn() function calls
    for match in re.findall(r'cn\s*\(\s*["\']([^"\']*)["\']', content, re.MULTILINE):
        classes.update(match.split())

    # Filter valid classes
    return {c for c in classes if c and re.match(r"^[a-zA-Z0-9_:-]+$", c)}


class ContentScanner:
    """Scans project files for Tailwind CSS classes."""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.patterns = get_content_patterns(config.project_root)

    def scan_files(self) -> set[str]:
        all_classes: set[str] = set()

        for pattern in self.patterns:
            if pattern.startswith("!"):
                continue

            for file in self.config.project_root.glob(pattern):
                if file.suffix not in {".py", ".html", ".js", ".ts", ".jsx", ".tsx"}:
                    continue

                try:
                    content = file.read_text(encoding="utf-8")
                    all_classes.update(extract_classes(content))
                except (UnicodeDecodeError, PermissionError):
                    continue

        return all_classes


class CSSBuilder:
    """CSS build orchestrator."""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.binary_manager = TailwindBinaryManager("latest")
        self.scanner = ContentScanner(config)

    def build(
        self,
        mode: BuildMode = BuildMode.DEVELOPMENT,
        watch: bool = False,
        scan_content: bool = True,
    ) -> BuildResult:
        """Build CSS with Tailwind."""
        start_time = time.time()

        try:
            binary_path = self.binary_manager.get_binary()

            # Scan for classes
            classes_found = None
            if scan_content:
                found = self.scanner.scan_files()
                classes_found = len(found)

            # Create temp directory for build
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create input CSS
                input_file = temp_path / "input.css"
                input_file.write_text(generate_css_input(self.config))

                # Ensure output dir exists
                self.config.css_output_absolute.parent.mkdir(
                    parents=True, exist_ok=True
                )

                # Build command
                cmd = [
                    str(binary_path),
                    "-i",
                    str(input_file),
                    "-o",
                    str(self.config.css_output_absolute),
                ]

                if mode == BuildMode.PRODUCTION:
                    cmd.append("--minify")
                if watch:
                    cmd.append("--watch")

                # Run build
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode != 0:
                    raise BuildError(
                        f"Tailwind failed: {result.stderr or 'Unknown error'}"
                    )

            # Calculate stats
            build_time = time.time() - start_time
            css_size = None
            if self.config.css_output_absolute.exists():
                css_size = self.config.css_output_absolute.stat().st_size

            return BuildResult(
                success=True,
                css_path=self.config.css_output_absolute,
                build_time=build_time,
                classes_found=classes_found,
                css_size_bytes=css_size,
            )

        except Exception as e:
            return BuildResult(success=False, error_message=str(e))
