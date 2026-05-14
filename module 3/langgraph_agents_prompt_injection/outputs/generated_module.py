import re
from typing import Any


def normalize_customer_name(value: Any) -> str:
    """Normalize a customer name for matching and display.

    Args:
        value: Customer name supplied by an upstream system.

    Returns:
        A normalized name with collapsed whitespace and title casing.

    Raises:
        TypeError: If value is not a string.
    """
    if not isinstance(value, str):
        raise TypeError("Customer name must be a string.")

    collapsed = re.sub(r"\s+", " ", value.strip())
    if not collapsed:
        return ""

    return collapsed.title()
