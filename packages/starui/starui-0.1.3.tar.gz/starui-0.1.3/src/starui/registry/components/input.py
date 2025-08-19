"""Input component matching shadcn/ui styling and behavior."""

from typing import Literal

from starhtml import FT
from starhtml import Input as BaseInput

from .utils import cn

InputType = Literal[
    "text",
    "password",
    "email",
    "number",
    "tel",
    "url",
    "search",
    "date",
    "datetime-local",
    "month",
    "time",
    "week",
    "color",
    "file",
]


def Input(
    type: InputType = "text",
    placeholder: str | None = None,
    value: str | None = None,
    name: str | None = None,
    id: str | None = None,
    disabled: bool = False,
    readonly: bool = False,
    required: bool = False,
    autofocus: bool = False,
    autocomplete: str | None = None,
    min: str | int | None = None,
    max: str | int | None = None,
    step: str | int | None = None,
    pattern: str | None = None,
    cls: str = "",
    class_name: str = "",
    **attrs,  # type: ignore
) -> FT:
    """
    Input component matching shadcn/ui styling and behavior.

    Args:
        type: Input type (text, email, password, etc.)
        placeholder: Placeholder text
        value: Initial value
        name: Form field name
        id: Element ID
        disabled: Whether input is disabled
        readonly: Whether input is read-only
        required: Whether input is required
        autofocus: Whether to autofocus on mount
        autocomplete: Autocomplete attribute
        min: Minimum value (for number/date inputs)
        max: Maximum value (for number/date inputs)
        step: Step value (for number inputs)
        pattern: Validation pattern (regex)
        cls: Additional CSS classes
        class_name: Alternative way to pass CSS classes
        **attrs: Additional HTML attributes including Datastar directives

    Returns:
        Input element
    """
    classes = cn(
        # Base styles
        "flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none",
        "border-input",
        "placeholder:text-muted-foreground",
        "selection:bg-primary selection:text-primary-foreground",
        "dark:bg-input/30",
        # File input styles
        "file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
        # Focus styles
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
        # Invalid styles
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
        # Disabled styles
        "disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50",
        # Responsive
        "md:text-sm",
        class_name,
        cls,
    )

    # Build input attributes
    input_attrs = {"type": type, "cls": classes, "data_slot": "input", **attrs}

    # Add optional attributes only if provided
    if placeholder:
        input_attrs["placeholder"] = placeholder
    if value is not None:
        input_attrs["value"] = value
    if name:
        input_attrs["name"] = name
    if id:
        input_attrs["id"] = id
    if disabled:
        input_attrs["disabled"] = disabled
    if readonly:
        input_attrs["readonly"] = readonly
    if required:
        input_attrs["required"] = required
    if autofocus:
        input_attrs["autofocus"] = autofocus
    if autocomplete:
        input_attrs["autocomplete"] = autocomplete
    if min is not None:
        input_attrs["min"] = str(min)
    if max is not None:
        input_attrs["max"] = str(max)
    if step is not None:
        input_attrs["step"] = str(step)
    if pattern:
        input_attrs["pattern"] = pattern

    return BaseInput(**input_attrs)


def InputWithLabel(
    label: str,
    type: InputType = "text",
    placeholder: str | None = None,
    value: str | None = None,
    name: str | None = None,
    id: str | None = None,
    disabled: bool = False,
    readonly: bool = False,
    required: bool = False,
    helper_text: str | None = None,
    error_text: str | None = None,
    cls: str = "",
    label_cls: str = "",
    input_cls: str = "",
    **attrs,
) -> FT:
    """
    Input with label and optional helper/error text.

    Args:
        label: Label text
        helper_text: Helper text below input
        error_text: Error message (makes input invalid)
        label_cls: CSS classes for label
        input_cls: CSS classes for input
        ... (all other Input args)

    Returns:
        Container with label and input
    """
    from starhtml import Div, Label, P, Span

    # Generate ID if not provided
    if not id:
        import uuid

        id = f"input_{str(uuid.uuid4())[:8]}"

    # Set aria-invalid if there's an error
    if error_text:
        attrs["aria_invalid"] = "true"

    return Div(
        Label(
            label,
            Span(" *", cls="text-destructive") if required else "",
            for_=id,
            cls=cn("block text-sm font-medium mb-1.5", label_cls),
        ),
        Input(
            type=type,
            placeholder=placeholder,
            value=value,
            name=name,
            id=id,
            disabled=disabled,
            readonly=readonly,
            required=required,
            cls=input_cls,
            **attrs,
        ),
        error_text and P(error_text, cls="text-sm text-destructive mt-1.5"),
        helper_text
        and not error_text
        and P(helper_text, cls="text-sm text-muted-foreground mt-1.5"),
        cls=cn("space-y-1.5", cls),
    )
