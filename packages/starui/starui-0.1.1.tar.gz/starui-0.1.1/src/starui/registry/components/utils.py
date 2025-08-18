"""Utility functions for components.

This module provides core utility functions used by components, including
class name composition (cn), class variance authority (cva), and component
styling helpers.
"""

from collections.abc import Callable
from typing import Any


def cn(*classes: Any) -> str:
    """Combine class names, filtering out falsy values."""
    result_classes: list[str] = []

    for cls in classes:
        if not cls:
            continue

        if isinstance(cls, str):
            result_classes.append(cls)
        elif isinstance(cls, dict):
            for class_name, condition in cls.items():
                if condition:
                    result_classes.append(str(class_name))
        elif isinstance(cls, list | tuple):
            result_classes.append(cn(*cls))
        else:
            result_classes.append(str(cls))

    return " ".join(result_classes)


def cva(
    base: str = "",
    variants: dict[str, dict[str, str]] | None = None,
    compound_variants: list[dict[str, Any]] | None = None,
    default_variants: dict[str, str] | None = None,
) -> Callable[..., str]:
    """Create a class variance authority function for component styling.

    Inspired by cva from class-variance-authority, this creates a function
    that generates class names based on variant props with support for
    compound variants and default values.

    Args:
        base: Base class names to always include.
        variants: Dictionary of variant configurations.
        compound_variants: List of compound variant rules.
        default_variants: Default values for variants.

    Returns:
        Function that generates class names based on variant props.

    Examples:
        >>> button_variants = cva(
        ...     "inline-flex items-center justify-center",
        ...     {
        ...         "variant": {
        ...             "primary": "bg-primary text-primary-foreground",
        ...             "secondary": "bg-secondary text-secondary-foreground"
        ...         },
        ...         "size": {
        ...             "sm": "h-8 px-3 text-xs",
        ...             "lg": "h-12 px-8 text-base"
        ...         }
        ...     },
        ...     compound_variants=[
        ...         {
        ...             "variant": "primary",
        ...             "size": "lg",
        ...             "class": "font-semibold"
        ...         }
        ...     ],
        ...     default_variants={"variant": "primary", "size": "sm"}
        ... )
        >>> button_variants()  # Uses defaults
        'inline-flex items-center justify-center bg-primary text-primary-foreground h-8 px-3 text-xs'
        >>> button_variants(variant="secondary", size="lg")
        'inline-flex items-center justify-center bg-secondary text-secondary-foreground h-12 px-8 text-base'
    """
    if variants is None:
        variants = {}
    if compound_variants is None:
        compound_variants = []
    if default_variants is None:
        default_variants = {}

    def variant_function(**props: Any) -> str:
        """Generate class names based on variant props."""
        classes = [base] if base else []

        # Merge default variants with provided props
        final_props = {**default_variants, **props}

        # Apply basic variants
        for variant_key, variant_values in variants.items():
            prop_value = final_props.get(variant_key)
            if prop_value and prop_value in variant_values:
                classes.append(variant_values[prop_value])

        # Apply compound variants
        for compound in compound_variants:
            compound_class = compound.get("class", "")
            if not compound_class:
                continue

            # Check if all conditions match
            matches = True
            for key, value in compound.items():
                if key == "class":
                    continue
                if final_props.get(key) != value:
                    matches = False
                    break

            if matches:
                classes.append(compound_class)

        return cn(*classes)

    return variant_function


def component_classes(
    base: str,
    modifiers: dict[str, bool] | None = None,
    size: str | None = None,
    variant: str | None = None,
) -> str:
    """Generate component classes with common patterns.

    A simplified helper for common component styling patterns.

    Args:
        base: Base class names.
        modifiers: Dictionary of modifier classes and their conditions.
        size: Size variant (sm, md, lg).
        variant: Style variant.

    Returns:
        Combined class string.

    Examples:
        >>> component_classes(
        ...     "btn",
        ...     modifiers={"disabled": True, "active": False},
        ...     size="sm",
        ...     variant="primary"
        ... )
        'btn disabled btn-sm btn-primary'
    """
    classes = [base]

    if modifiers:
        for modifier, condition in modifiers.items():
            if condition:
                classes.append(modifier)

    if size:
        classes.append(f"{base}-{size}")

    if variant:
        classes.append(f"{base}-{variant}")

    return cn(*classes)


def responsive_classes(base: str, breakpoints: dict[str, str] | None = None) -> str:
    """Generate responsive class names.

    Args:
        base: Base class for mobile-first.
        breakpoints: Dictionary of breakpoint prefixes and their classes.

    Returns:
        Combined responsive class string.

    Examples:
        >>> responsive_classes("text-sm", {"md": "text-base", "lg": "text-lg"})
        'text-sm md:text-base lg:text-lg'
    """
    classes = [base]

    if breakpoints:
        for breakpoint, class_name in breakpoints.items():
            classes.append(f"{breakpoint}:{class_name}")

    return cn(*classes)


def focus_ring(color: str = "ring-primary", size: str = "2") -> str:
    """Generate focus ring classes.

    Args:
        color: Ring color class.
        size: Ring width.

    Returns:
        Focus ring class string.

    Examples:
        >>> focus_ring()
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2'
        >>> focus_ring("ring-red-500", "4")
        'focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-red-500 focus-visible:ring-offset-2'
    """
    return cn(
        "focus-visible:outline-none",
        f"focus-visible:ring-{size}",
        f"focus-visible:{color}",
        "focus-visible:ring-offset-2",
    )


def transition_classes(
    properties: str | list[str] = "all",
    duration: str = "150",
    timing: str = "ease-in-out",
) -> str:
    """Generate transition classes.

    Args:
        properties: CSS properties to transition (string or list).
        duration: Transition duration in ms.
        timing: Timing function.

    Returns:
        Transition class string.

    Examples:
        >>> transition_classes()
        'transition-all duration-150 ease-in-out'
        >>> transition_classes(["colors", "opacity"], "300")
        'transition-colors transition-opacity duration-300 ease-in-out'
    """
    if isinstance(properties, str):
        transition = f"transition-{properties}"
    else:
        transition = " ".join(f"transition-{prop}" for prop in properties)

    return cn(transition, f"duration-{duration}", timing)


def datastar_attrs(**attrs: Any) -> dict[str, str]:
    """Convert Datastar attributes from Python naming to HTML format.

    Converts underscore-separated Python attribute names to kebab-case
    HTML attributes suitable for Datastar.

    Args:
        **attrs: Datastar attributes with Python naming.

    Returns:
        Dictionary of HTML-formatted attributes.

    Examples:
        >>> datastar_attrs(data_action="click", data_target="#modal")
        {'data-action': 'click', 'data-target': '#modal'}
        >>> datastar_attrs(data_on_click="showModal", aria_label="Close")
        {'data-on-click': 'showModal', 'aria-label': 'Close'}
    """
    result = {}

    for key, value in attrs.items():
        # Convert Python snake_case to HTML kebab-case
        html_key = key.replace("_", "-")
        result[html_key] = str(value)

    return result


def merge_props(defaults: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Merge component props with defaults.

    Args:
        defaults: Default prop values.
        overrides: Props to override defaults.

    Returns:
        Merged props dictionary.

    Examples:
        >>> merge_props(
        ...     {"variant": "default", "size": "md", "disabled": False},
        ...     {"variant": "primary", "disabled": True}
        ... )
        {'variant': 'primary', 'size': 'md', 'disabled': True}
    """
    return {**defaults, **overrides}
