from typing import List, Literal, TypedDict, Union

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.contact_endpoint import (
    ContactEndpoint,
    ContactEndpoints,
)


class ContactEndpointListQuery(TypedDict, total=False):
    _type: Literal["EmailEndpoint", "TelephonyEndpoint"]


class ContactEndpointResource(DixaResource):
    """
    https://docs.dixa.io/openapi/dixa-api/v1/tag/Contact-Endpoints/
    """

    resource = "contact-endpoints"
    dixa_version: DixaVersion = "v1"

    def get(self, contact_endpoint_id: str) -> ContactEndpoint:
        """Get contact endpoint.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Contact-Endpoints/#tag/Contact-Endpoints/operation/getContact-endpointsContactendpointid
        """
        data = self.client.get(f"{self._url}/{contact_endpoint_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        for return_cls in ContactEndpoints:
            try:
                return return_cls(**data)
            except TypeError:
                continue
        else:
            raise DixaAPIError(
                f"Expected one of {ContactEndpoints}, got {type(data).__name__}"
            )

    def list(
        self, query: Union[ContactEndpointListQuery, None] = None
    ) -> List[ContactEndpoint]:
        """List contact endpoints.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Contact-Endpoints/#tag/Contact-Endpoints/operation/getContact-endpoints
        """
        data = self.client.paginate(self._url, query=query)
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        results = []
        for elem in data:
            for return_cls in ContactEndpoints:
                try:
                    results.append(return_cls(**elem))
                    break
                except TypeError:
                    continue
            else:
                raise DixaAPIError(
                    f"Expected one of {ContactEndpoints}, got {type(data).__name__}"
                )
        return results
