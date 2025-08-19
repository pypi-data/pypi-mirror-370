"""
Label component - Form field labels.
Based on: https://github.com/shadcn-ui/ui/blob/main/apps/www/registry/new-york/ui/label.tsx
"""

from starhtml import FT
from starhtml import Label as HtmlLabel

from .utils import cn


def Label(
    *children,
    cls: str = "",
    class_name: str = "",
    **attrs,
) -> FT:
    """
    Label component - pixel-perfect shadcn/ui copy.

    A semantic label element with proper styling for form fields.
    Supports disabled states and proper accessibility attributes.
    """
    return HtmlLabel(
        *children,
        data_slot="label",
        cls=cn(
            "flex items-center gap-2 text-sm leading-none font-medium select-none",
            "group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50",
            "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
            class_name,
            cls,
        ),
        **attrs,
    )
