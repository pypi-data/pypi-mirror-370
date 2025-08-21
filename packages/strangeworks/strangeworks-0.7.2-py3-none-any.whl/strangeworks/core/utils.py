"""utils.py."""
from typing import Optional


def is_empty_str(s: str) -> bool:
    """Check if string is empty.

    A string is considered to be empty if any one of the following conditions are true:
        - it is set to `None` or
        - consists exclusively of spaces
     - is equal to `""`
    """
    return s is None or s.strip() == ""


def fix_str_attr(attr: str) -> Optional[str]:
    """Fix Attribute Name.

    Removes leading and trailing whitespaces and converts to lower-case.

    Parameters
    ----------
    attr: str
        Attribute value

    Returns
    -------
    :str
        adjusted attribute value
    """
    if attr is None:
        return None
    return attr.strip().lower()
