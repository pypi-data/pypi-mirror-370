"""gql.py."""

from strangeworks_core.platform.gql import API, APIInfo


class SDKAPI(API):
    """Wrapper for API class to provide access to the SDK API."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        **kwargs,
    ):
        """Initialize SDK API."""
        kwargs.pop("api_type") if "api_type" in kwargs else None
        super().__init__(
            api_key=api_key, base_url=base_url, api_type=APIInfo.SDK, **kwargs
        )
