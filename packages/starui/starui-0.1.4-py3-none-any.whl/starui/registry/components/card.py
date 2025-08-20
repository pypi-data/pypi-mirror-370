"""Card component matching shadcn/ui styling and behavior."""

from starhtml import FT, Div

from .utils import cn


def Card(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Card root component.

    Args:
        *children: Card content (typically CardHeader, CardContent, CardFooter)
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes including Datastar directives

    Returns:
        Card container element
    """
    classes = cn(
        "bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm",
        class_name,
        cls,
    )

    return Div(*children, cls=classes, data_slot="card", **attrs)


def CardHeader(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Card header component.

    Args:
        *children: Header content (typically CardTitle, CardDescription, CardAction)
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes

    Returns:
        Card header element
    """
    classes = cn(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
        class_name,
        cls,
    )

    return Div(*children, cls=classes, data_slot="card-header", **attrs)


def CardTitle(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Card title component.

    Args:
        *children: Title content
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes

    Returns:
        Card title element
    """
    classes = cn("leading-none font-semibold", class_name, cls)

    return Div(*children, cls=classes, data_slot="card-title", **attrs)


def CardDescription(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Card description component.

    Args:
        *children: Description content
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes

    Returns:
        Card description element
    """
    classes = cn("text-muted-foreground text-sm", class_name, cls)

    return Div(*children, cls=classes, data_slot="card-description", **attrs)


def CardAction(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Card action component for header actions.

    Args:
        *children: Action content (typically buttons or icons)
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes

    Returns:
        Card action element
    """
    classes = cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        class_name,
        cls,
    )

    return Div(*children, cls=classes, data_slot="card-action", **attrs)


def CardContent(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Card content component.

    Args:
        *children: Main content of the card
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes

    Returns:
        Card content element
    """
    classes = cn("px-6", class_name, cls)

    return Div(*children, cls=classes, data_slot="card-content", **attrs)


def CardFooter(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Card footer component.

    Args:
        *children: Footer content (typically buttons or actions)
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes

    Returns:
        Card footer element
    """
    classes = cn("flex items-center px-6 [.border-t]:pt-6", class_name, cls)

    return Div(*children, cls=classes, data_slot="card-footer", **attrs)
