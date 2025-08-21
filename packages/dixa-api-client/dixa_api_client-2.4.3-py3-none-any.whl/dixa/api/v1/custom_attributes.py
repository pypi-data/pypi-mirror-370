from typing import List

from dixa.api import DixaResource, DixaVersion
from dixa.model.v1.custom_attribute import CustomAttributeDefinition


class CustomAttributeResource(DixaResource):
    """
    https://docs.dixa.io/openapi/dixa-api/v1/tag/Custom-Attributes/
    """

    resource = "custom-attributes"
    dixa_version: DixaVersion = "v1"

    def list(self) -> List[CustomAttributeDefinition]:
        """List custom attributes definitions.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Custom-Attributes/#tag/Custom-Attributes/operation/getCustom-attributes
        """
        return self.client.paginate(self._url)
