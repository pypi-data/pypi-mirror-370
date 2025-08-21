from typing import Literal

from dixa.client import DixaClient

DixaVersion = Literal["v1", "beta"]


class DixaResource:
    """Generic Dixa API resource."""

    base_url = "https://dev.dixa.io"
    resource = None
    dixa_version: DixaVersion = "v1"

    def __init__(self, client: DixaClient):
        self.client = client

    @property
    def _url(self) -> str:
        return f"{self.base_url}/{self.dixa_version}/{self.resource}"
