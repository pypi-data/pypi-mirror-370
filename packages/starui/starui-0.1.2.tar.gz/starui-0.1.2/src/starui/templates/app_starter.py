"""StarHTML app starter template."""

from pathlib import Path

from ..config import ProjectConfig

APP_TEMPLATE = """\
from starhtml import *

styles = Link(rel="stylesheet", href="/{css_path}", type="text/css")

app, rt = star_app(
    hdrs=(styles,),
    htmlkw={{"lang": "en", "dir": "ltr"}},
    bodykw={{"cls": "min-h-screen bg-gray-100 dark:bg-gray-900"}}
)

@rt("/")
def get():
    return Div(
        Div(
            H1("Nothing to see here yet...",
               cls="text-2xl font-bold mb-2 text-gray-900 dark:text-white"),
            P("But your StarHTML app is running!",
              cls="text-base text-gray-600 dark:text-gray-400"),
            cls="text-center"
        ),
        cls="min-h-screen flex items-center justify-center"
    )

if __name__ == "__main__":
    serve(port=8000)
"""


def generate_app_starter(
    config: ProjectConfig | None = None,
    app_name: str = "app.py",
    include_css_link: bool = True,
    include_components_example: bool = True,
) -> str:
    """Generate a starter StarHTML app."""
    if config is None:
        config = ProjectConfig(
            project_root=Path.cwd(),
            css_output=Path("starui.css"),
            component_dir=Path("components/ui"),
        )

    return APP_TEMPLATE.format(css_path=str(config.css_output))
