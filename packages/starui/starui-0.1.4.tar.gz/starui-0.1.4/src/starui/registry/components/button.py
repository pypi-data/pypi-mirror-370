"""Button component matching shadcn/ui styling and behavior."""

from typing import Any, Literal

from starhtml import FT
from starhtml import Button as BaseButton

from .utils import cn, cva

ButtonVariant = Literal[
    "default", "destructive", "outline", "secondary", "ghost", "link"
]
ButtonSize = Literal["default", "sm", "lg", "icon"]


button_variants = cva(
    base="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
    variants={
        "variant": {
            "default": "bg-primary text-primary-foreground shadow hover:bg-primary/90",
            "destructive": "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
            "outline": "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
            "secondary": "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
            "ghost": "hover:bg-accent hover:text-accent-foreground",
            "link": "text-primary underline-offset-4 hover:underline",
        },
        "size": {
            "default": "h-10 px-4 py-2",
            "sm": "h-9 rounded-md px-3",
            "lg": "h-11 rounded-md px-8",
            "icon": "h-10 w-10",
        },
    },
    default_variants={"variant": "default", "size": "default"},
)


def Button(
    *children: Any,  # HTML content: str, int, FT objects, etc.
    variant: ButtonVariant = "default",
    size: ButtonSize = "default",
    class_name: str = "",
    disabled: bool = False,
    type: Literal["button", "submit", "reset"] = "button",
    cls: str = "",
    **attrs: Any,  # Additional HTML attributes
) -> FT:
    """Button component with pragmatic typing and shadcn/ui styling."""
    classes = cn(button_variants(variant=variant, size=size), class_name, cls)

    return BaseButton(*children, cls=classes, disabled=disabled, type=type, **attrs)
