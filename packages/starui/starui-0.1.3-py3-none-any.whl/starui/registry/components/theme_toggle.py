"""Theme toggle component using Datastar for reactivity.

Dependencies: button
"""

from starhtml import FT, Div, Icon, Span
from starhtml.datastar import ds_on_click, ds_on_load, ds_show, ds_signals

from .button import Button


def ThemeToggle(alt_theme="dark", default_theme="light", **attrs) -> FT:
    """Reactive theme toggle with smart .dark class and data-theme support."""

    apply_theme = f"""
    const html = document.documentElement;
    const usesDarkClass = html.classList.contains('{alt_theme}') || html.classList.contains('{default_theme}');

    if ($isDark) {{
        usesDarkClass && html.classList.add('{alt_theme}');
        html.setAttribute('data-theme', '{alt_theme}');
    }} else {{
        usesDarkClass && html.classList.remove('{alt_theme}');
        html.setAttribute('data-theme', '{default_theme}');
    }}
    """

    return Div(
        Button(
            Span(Icon("ph:moon-bold", cls="h-4 w-4"), ds_show("!$isDark")),
            Span(Icon("ph:sun-bold", cls="h-4 w-4"), ds_show("$isDark")),
            ds_on_click(
                f"$isDark = !$isDark; {apply_theme} localStorage.setItem('theme', $isDark ? '{alt_theme}' : '{default_theme}');"
            ),
            variant="ghost",
            aria_label="Toggle theme",
            cls="h-9 px-4 py-2 flex-shrink-0",
        ),
        ds_signals(isDark=False),
        ds_on_load(f"""
        const saved = localStorage.getItem('theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const html = document.documentElement;

        $isDark = saved === '{alt_theme}' || (!saved && systemDark) ||
                  html.classList.contains('{alt_theme}') ||
                  html.getAttribute('data-theme') === '{alt_theme}';

        {apply_theme}
        """),
        **attrs,
    )
