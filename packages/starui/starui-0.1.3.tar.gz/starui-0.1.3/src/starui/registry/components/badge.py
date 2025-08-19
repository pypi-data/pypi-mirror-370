"""Badge component matching shadcn/ui styling and behavior."""

from typing import Literal

from starhtml import FT, A, Span

from .utils import cn, cva

BadgeVariant = Literal["default", "secondary", "destructive", "outline"]


badge_variants = cva(
    base="inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
    variants={
        "variant": {
            "default": "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
            "secondary": "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
            "destructive": "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
            "outline": "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
        }
    },
    default_variants={"variant": "default"},
)


def Badge(
    *children,
    variant: BadgeVariant = "default",
    href: str | None = None,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Badge component matching shadcn/ui styling and behavior.

    Args:
        *children: Badge content (text, icons, etc.)
        variant: Visual style variant
        href: If provided, renders as link (anchor tag)
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes including Datastar directives

    Returns:
        Badge element (span or anchor based on href)
    """
    classes = cn(badge_variants(variant=variant), class_name, cls)

    # If href is provided, render as anchor tag for clickable badges
    if href:
        return A(*children, href=href, cls=classes, data_slot="badge", **attrs)

    # Default to span element
    return Span(*children, cls=classes, data_slot="badge", **attrs)


def ClickableBadge(
    *children,
    variant: BadgeVariant = "default",
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Clickable badge with Datastar click handler.

    Args:
        *children: Badge content
        variant: Visual style variant
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes (including ds_on_click)

    Returns:
        Clickable badge element with cursor-pointer
    """
    classes = cn(
        badge_variants(variant=variant),
        "cursor-pointer",  # Add cursor pointer for clickable badges
        class_name,
        cls,
    )

    return Span(
        *children,
        cls=classes,
        data_slot="badge",
        tabindex="0",  # Make keyboard accessible
        role="button",  # Indicate it's interactive
        **attrs,
    )
