def build_full_name(first_name: str = None, last_name: str = None) -> str:
    """
    Build a full name from first and last name components.

    Args:
        first_name: The first name (optional)
        last_name: The last name (optional)

    Returns:
        A formatted full name string with proper spacing
    """
    names = [name.strip() for name in [first_name, last_name] if name and name.strip()]
    return ' '.join(names)
