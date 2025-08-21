"""utils.py."""


def is_empty_str(s: str) -> bool:
    """Check if string is empty.

    A string is considered to be empty if any one of the following conditions are true:
        - it is set to `None` or
        - consists exclusively of spaces
     - is equal to `""`
    """
    return not s or s == "" or s.isspace()
