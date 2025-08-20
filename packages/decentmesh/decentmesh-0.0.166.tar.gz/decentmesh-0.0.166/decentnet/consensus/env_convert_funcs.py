def e2b(value):
    """
    Convert a string or other types representing booleans to a Python boolean.

    Args:
        value: The value (usually from an environment variable) to convert to a boolean.

    Returns:
        bool: The converted boolean value.

    Raises:
        ValueError: If the value cannot be interpreted as a boolean.
    """
    truthy_values = {"true", "1", "t", "yes", "y", "on"}
    falsy_values = {"false", "0", "f", "no", "n", "off"}

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value_lower = value.strip().lower()  # Strip any extra whitespace and normalize case
        if value_lower in truthy_values:
            return True
        elif value_lower in falsy_values:
            return False

    # Raise an error for anything that can"t be interpreted as a boolean
    raise ValueError(f"Cannot interpret {value} as a boolean.")
