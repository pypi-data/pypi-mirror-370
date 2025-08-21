"""error.py."""
from typing import Optional


class StrangeworksError(Exception):
    """Standard Strangeworks Exception.

    This is the standard Strangeworks exception type utilized
    in both API responses to errors or from the SDK implementation
    when a known error is captured.
    """

    def __init__(
        self,
        message: str = "",
        help_page_url: str = "",
    ):
        self.message = message
        self.help_page_url = help_page_url
        super().__init__(self.message)

    @classmethod
    def authentication_error(cls, message: str = None, help_page_url: str = None):
        return cls.__builder(
            message=message,
            default_message=(
                "authentication is invalid, utilize client.authenticate() to refresh"
            ),
            help_page_url=help_page_url,
        )

    @classmethod
    def invalid_argument(cls, message: str = None, help_page_url: str = None):
        return cls.__builder(
            message=message,
            default_message="invalid argument provided",
            help_page_url=help_page_url,
        )

    @classmethod
    def not_implemented(cls, help_page_url: str = None):
        return cls.__builder(
            message="This feature is not yet implemented",
            help_page_url=help_page_url,
        )

    @classmethod
    def timeout(cls, message: Optional[str] = None, help_page_url: str = None):
        return cls.__builder(
            default_message="Timeout attempting request",
            message=message,
            help_page_url=help_page_url,
        )

    @classmethod
    def bad_response(
        cls, message: Optional[str] = None, help_page_url: Optional[str] = None
    ):
        return cls.__builder(
            message=message,
            default_message="invalid response from server",
            help_page_url=help_page_url,
        )

    @classmethod
    def server_error(
        cls,
        message: Optional[str] = None,
        query_id: Optional[int] = None,
        help_page_url: Optional[str] = None,
    ):
        return cls.__builder(
            message=message + f" Query ID: {query_id}.",
            default_message="server error",
            help_page_url=help_page_url,
        )

    @classmethod
    def __builder(
        cls,
        message: str = None,
        help_page_url: str = None,
        default_message: str = "",
        default_help_page_url: str = "",
    ):
        return StrangeworksError(
            message=message or default_message,
            help_page_url=help_page_url or default_help_page_url,
        )
