from typing import List, TypedDict

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.webhook_subscription import (
    Authorization,
    Event,
    EventDeliveryLog,
    EventDeliveryStatus,
    WebhookSubscription,
)


class _WebhookCreateBodyRequired(TypedDict):
    name: str
    url: str


class _WebhookCreateBodyOptional(TypedDict, total=False):
    authorization: "Authorization"
    enabled: bool
    events: List["Event"]


class WebhookCreateBody(_WebhookCreateBodyRequired, _WebhookCreateBodyOptional):
    pass


class WebhookPatchBody(TypedDict, total=False):
    authorization: Authorization
    enabled: bool
    events: List[Event]
    name: str
    url: str


class WebhookResource(DixaResource):
    """
    https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/
    """

    resource = "webhooks"
    dixa_version: DixaVersion = "v1"

    def create(self, body: WebhookCreateBody) -> WebhookSubscription:
        """Create a webhook.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/#tag/Webhooks/operation/postWebhooks
        """
        data = self.client.post(self._url, body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return WebhookSubscription(**data)

    def delete(self, webhook_subscription_id: str):
        """Delete a webhook.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/#tag/Webhooks/operation/deleteWebhooksWebhooksubscriptionid
        """
        return self.client.delete(f"{self._url}/{webhook_subscription_id}")

    def list_(self) -> List[WebhookSubscription]:
        """List webhooks.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/#tag/Webhooks/operation/getWebhooks
        """
        return self.client.paginate(self._url)

    def patch(
        self, webhook_subscription_id: str, body: WebhookPatchBody
    ) -> WebhookSubscription:
        """Update a webhook.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/#tag/Webhooks/operation/patchWebhooksWebhooksubscriptionid
        """
        data = self.client.patch(f"{self._url}/{webhook_subscription_id}", body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return WebhookSubscription(**data)

    def get(self, webhook_subscription_id: str) -> WebhookSubscription:
        """Get a webhook.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/#tag/Webhooks/operation/getWebhooksWebhooksubscriptionid
        """
        data = self.client.get(f"{self._url}/{webhook_subscription_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return WebhookSubscription(**data)

    def list_event_logs(
        self, webhook_subscription_id: str, event: str
    ) -> List[EventDeliveryLog]:
        """Get event logs.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/#tag/Webhooks/operation/getWebhooksWebhooksubscriptionidDelivery-statusLogsEvent
        """
        return self.client.paginate(
            f"{self._url}/{webhook_subscription_id}/delivery-status/logs/{event}"
        )

    def list_delivery_statuses(
        self, webhook_subscription_id: str
    ) -> List[EventDeliveryStatus]:
        """Get delivery statuses.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Webhooks/#tag/Webhooks/operation/getWebhooksWebhooksubscriptionidDelivery-status
        """
        return self.client.paginate(
            f"{self._url}/{webhook_subscription_id}/delivery-status"
        )
