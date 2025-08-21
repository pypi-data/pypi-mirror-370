from typing import List, TypedDict

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.tag import Tag


class _TagCreateBodyRequired(TypedDict):
    name: str


class _TagCreateBodyOptional(TypedDict, total=False):
    color: str


class TagCreateBody(_TagCreateBodyRequired, _TagCreateBodyOptional):
    pass


class TagResource(DixaResource):
    """
    https://docs.dixa.io/openapi/dixa-api/v1/tag/Tags/
    """

    resource = "tags"
    dixa_version: DixaVersion = "v1"

    def activate(self, tag_id: str):
        """Activate a tag.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Tags/#tag/Tags/operation/patchTagsTagidActivate
        """
        return self.client.patch(f"{self._url}/{tag_id}/activate")

    def create(self, body: TagCreateBody) -> Tag:
        """Create a tag.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Tags/#tag/Tags/operation/postTags
        """
        data = self.client.post(self._url, body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Tag(**data)

    def deactivate(self, tag_id: str):
        """Deactivate a tag.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Tags/#tag/Tags/operation/patchTagsTagidDeactivate
        """
        return self.client.patch(f"{self._url}/{tag_id}/deactivate")

    def get(self, tag_id: str) -> Tag:
        """Get a tag by id.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Tags/#tag/Tags/operation/getTagsTagid
        """
        data = self.client.get(f"{self._url}/{tag_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Tag(**data)

    def list_(self) -> List[Tag]:
        """List tags.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Tags/#tag/Tags/operation/getTags
        """
        return self.client.paginate(self._url)
