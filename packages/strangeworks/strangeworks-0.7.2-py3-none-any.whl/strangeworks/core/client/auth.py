"""auth.py."""

from strangeworks_core.platform.auth import get_token as get_tok


def get_token(api_key: str, base_url: str) -> str:
    """Obtain a bearer token using an API key.

    Parameters
    ----------
    api_key: str
        Users API key. Obtained from users workspace.
    base_url: str
        Base URL to access auth endpoint on platform.

    Returns
    -------
    : str
        A JWT token which can be used to access workspace resources, files, etc.
    """
    return get_tok(api_key=api_key, base_url=base_url, auth_url="users/token")
