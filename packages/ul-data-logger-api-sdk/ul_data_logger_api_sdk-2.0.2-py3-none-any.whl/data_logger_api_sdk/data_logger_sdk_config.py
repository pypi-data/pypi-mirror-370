from typing import NamedTuple


class DataLoggerApiSdkConfig(NamedTuple):
    api_url: str
    api_token: str | None = None
    cache_ttl_s: int = 3600
