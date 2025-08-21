from typing import Dict, List, Literal, Optional, TypedDict, Union

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.activity_log import ActivityLog
from dixa.model.v1.anonymization import AnonymizationRequest
from dixa.model.v1.conversation import (
    BrowserInfo,
    Channel,
    Conversation,
    ConversationCustomAttribute,
    ConversationFlow,
    ConversationRating,
    ConversationResponse,
    ConversationSearchHit,
    ConversationTypes,
)
from dixa.model.v1.internal_note import InternalNote
from dixa.model.v1.message import Direction, File, Message
from dixa.model.v1.tag import Tag


class _ConversationAddInternalNoteBodyRequired(TypedDict):
    message: str


class _ConversationAddInternalNoteBodyOptional(TypedDict, total=False):
    agentId: str
    createdAt: str


class ConversationAddInternalNoteBody(
    _ConversationAddInternalNoteBodyRequired, _ConversationAddInternalNoteBodyOptional
):
    pass


class ConversationAddMessageBodyContentText(TypedDict):
    value: str
    _type: Literal["Text"]


class ConversationAddMessageBodyContentHtml(TypedDict):
    value: str
    _type: Literal["Html"]


ConversationAddMessageBodyContent = Union[
    ConversationAddMessageBodyContentText, ConversationAddMessageBodyContentHtml
]


class _ConversationAddMessageInboundBodyRequired(TypedDict):
    content: ConversationAddMessageBodyContent


class _ConversationAddMessageInboundBodyOptional(TypedDict, total=False):
    attachments: List["File"]
    externalId: str
    integrationEmail: str
    _type: Literal["Inbound"]


class ConversationAddMessageInboundBody(
    _ConversationAddMessageInboundBodyRequired,
    _ConversationAddMessageInboundBodyOptional,
):
    pass


class _ConversationAddMessageOutboundBodyRequired(TypedDict):
    agentId: str
    content: ConversationAddMessageBodyContent


class _ConversationAddMessageOutboundBodyOptional(TypedDict, total=False):
    attachments: List["File"]
    bcc: List[str]
    cc: List[str]
    externalId: str
    integrationEmail: str
    _type: Literal["Outbound"]


class ConversationAddMessageOutboundBody(
    _ConversationAddMessageOutboundBodyRequired,
    _ConversationAddMessageOutboundBodyOptional,
):
    pass


ConversationAddMessageBody = Union[
    ConversationAddMessageInboundBody, ConversationAddMessageOutboundBody
]


class _ConversationClaimBodyRequired(TypedDict):
    agentId: str


class _ConversationClaimBodyOptional(TypedDict, total=False):
    force: bool


class ConversationClaimBody(
    _ConversationClaimBodyRequired, _ConversationClaimBodyOptional
):
    pass


class ConversationCloseBody(TypedDict, total=False):
    userId: str


class ConversationCallbackCreateBody(TypedDict):
    contactEndpointId: str
    direction: Direction
    queueId: str
    requesterId: str
    _type: Literal["Callback"]


class ConversationChatCreateBody(TypedDict):
    browserInfo: Optional[BrowserInfo]
    language: Optional[str]
    message: ConversationAddMessageBody
    requesterId: str
    widgetId: str
    _type: Literal["Chat"]


class ConversationContactFormCreateBody(TypedDict):
    emailIntegrationId: str
    language: Optional[str]
    message: ConversationAddMessageBody
    requesterId: str
    subject: str
    _type: Literal["ContactForm"]


class ConversationEmailCreateBody(TypedDict):
    emailIntegrationId: str
    language: Optional[str]
    message: ConversationAddMessageBody
    requesterId: str
    subject: str
    _type: Literal["Email"]


class ConversationSmsCreateBody(TypedDict):
    contactEndpointId: str
    message: ConversationAddMessageBody
    requesterId: str
    _type: Literal["Sms"]


ConversationCreateBody = Union[
    ConversationCallbackCreateBody,
    ConversationChatCreateBody,
    ConversationContactFormCreateBody,
    ConversationEmailCreateBody,
    ConversationSmsCreateBody,
]


class ConversationListFlowsQuery(TypedDict):
    channel: Channel


ConversationPatchCustomAttributesBody = Dict[str, Union[str, List[str]]]


class ConversationReopenBody(TypedDict, total=False):
    userId: str


class ConversationSearchQueryQueryFilterConditionFieldOperatorIsEmpty(TypedDict):
    _type: Literal["IsEmpty"]


class ConversationSearchQueryQueryFilterConditionFieldOperatorIsNotEmpty(TypedDict):
    _type: Literal["IsNotEmpty"]


class ConversationSearchQueryQueryFilterConditionFieldOperatorIsNotOneOf(TypedDict):
    values: List[str]
    _type: Literal["IsNotOneOf"]


class ConversationSearchQueryQueryFilterConditionFieldOperatorIsOneOf(TypedDict):
    values: List[str]
    _type: Literal["IsOneOf"]


ConversationSearchQueryQueryFilterConditionFieldOperator = Union[
    ConversationSearchQueryQueryFilterConditionFieldOperatorIsEmpty,
    ConversationSearchQueryQueryFilterConditionFieldOperatorIsNotEmpty,
    ConversationSearchQueryQueryFilterConditionFieldOperatorIsNotOneOf,
    ConversationSearchQueryQueryFilterConditionFieldOperatorIsOneOf,
]


class ConversationSearchQueryQueryFilterConditionField(TypedDict):
    operator: ConversationSearchQueryQueryFilterConditionFieldOperator
    _type: Literal[
        "AgentId",
        "AssignedDate",
        "Channel",
        "ClosedDate",
        "ContactId",
        "ConversationId",
        "CreationDate",
        "CustomAttribute",
        "Direction",
        "Duration",
        "LastActivity",
        "LastMessage",
        "QueueId",
        "Status",
        "TagId",
    ]


class ConversationSearchQueryFilterCondition(TypedDict):
    field: ConversationSearchQueryQueryFilterConditionField


class ConversationSearchQueryFilter(TypedDict):
    conditions: List[ConversationSearchQueryFilterCondition]
    strategy: Literal["All", "Any"]


class ConversationSearchQueryQuery(TypedDict):
    exactMatch: Optional[bool]
    query: str


class ConversationSearchQuery(TypedDict):
    filters: List[ConversationSearchQueryFilter]
    query: ConversationSearchQueryQuery


class _ConversationTransferBodyRequired(TypedDict):
    queueId: str


class _ConversationTransferBodyOptional(TypedDict, total=False):
    userId: str


class ConversationTransferBody(
    _ConversationTransferBodyRequired, _ConversationTransferBodyOptional
):
    pass


class ConversationResource(DixaResource):
    """
    https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/
    """

    resource = "conversations"
    dixa_version: DixaVersion = "v1"

    def add_internal_note(
        self, conversation_id: str, body: ConversationAddInternalNoteBody
    ) -> InternalNote:
        """Add an internal note to a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/postConversationsConversationidNotes
        """
        data = self.client.post(f"{self._url}/{conversation_id}/notes", body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return InternalNote(**data)

    def add_internal_notes(
        self, conversation_id: str, body: List[ConversationAddInternalNoteBody]
    ) -> List[InternalNote]:
        """Add internal notes to a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/postConversationsConversationidNotesBulk
        """
        data = self.client.post(
            f"{self._url}/{conversation_id}/notes/bulk", {"data": body}, expected=list
        )
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        return [InternalNote(**item) for item in data]

    def add_message(
        self, conversation_id: str, body: ConversationAddMessageBody
    ) -> Message:
        """Add a message to a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/postConversationsConversationidMessages
        """
        data = self.client.post(f"{self._url}/{conversation_id}/messages", body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Message(**data)

    def anonymize(self, conversation_id: str) -> AnonymizationRequest:
        """Anonymize a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/postConversationsConversationidAnonymize
        """
        data = self.client.patch(f"{self._url}/{conversation_id}/anonymize")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return AnonymizationRequest(**data)

    def anonymize_message(
        self, conversation_id: str, message_id: str
    ) -> AnonymizationRequest:
        """Anonymize message in a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/patchConversationsConversationidMessagesMessageidAnonymize
        """
        data = self.client.patch(
            f"{self._url}/{conversation_id}/messages/{message_id}/anonymize"
        )
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return AnonymizationRequest(**data)

    def claim(self, conversation_id: str, body: ConversationClaimBody):
        """Claim a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/putConversationsConversationidClaim
        """
        return self.client.put(f"{self._url}/{conversation_id}/claim", body)

    def close(self, conversation_id: str, body: ConversationCloseBody):
        """Close a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/postConversationsConversationidClose
        """
        return self.client.put(f"{self._url}/{conversation_id}/close", body)

    def create(self, body: ConversationCreateBody) -> ConversationResponse:
        """Create a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/postConversations
        """
        data = self.client.post(self._url, body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")

        for conversation_type in ConversationTypes:
            try:
                return conversation_type(**data)
            except TypeError:
                continue

        raise DixaAPIError("Unknown conversation type", data)

    def get(self, conversation_id: str) -> Conversation:
        """Get an conversation by id.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsConversationid
        """
        data = self.client.get(f"{self._url}/{conversation_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")

        for conversation_type in ConversationTypes:
            try:
                return conversation_type(**data)
            except TypeError:
                continue

        raise DixaAPIError(
            f"Expected one of {ConversationTypes}, got {type(data).__name__}"
        )

    def list_activity_logs(self, conversation_id: str) -> List[ActivityLog]:
        """List activity logs.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsConversationidActivitylog
        """
        return self.client.paginate(f"{self._url}/{conversation_id}/activitylog")

    def list_flows(
        self,
        conversation_id: str,
        query: Union[ConversationListFlowsQuery, None] = None,
    ) -> List[ConversationFlow]:
        """List flows.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsFlows
        """
        return self.client.paginate(f"{self._url}/{conversation_id}/flows", query)

    def list_internal_notes(self, conversation_id: str) -> List[InternalNote]:
        """List internal notes.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsConversationidNotes
        """
        return self.client.paginate(f"{self._url}/{conversation_id}/notes")

    def list_linked_conversations(self, conversation_id: str) -> List[Conversation]:
        """List linked conversations.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsConversationidLinked
        """
        data = self.client.paginate(f"{self._url}/{conversation_id}/linked")
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        results = []
        for elem in data:
            for return_cls in ConversationTypes:
                try:
                    results.append(return_cls(**elem))
                    break
                except TypeError:
                    continue
            else:
                raise DixaAPIError(
                    f"Expected one of {ConversationTypes}, got {type(data).__name__}"
                )
        return results

    def list_messages(self, conversation_id: str) -> List[Message]:
        """List messages.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsConversationidMessages
        """
        return self.client.paginate(f"{self._url}/{conversation_id}/messages")

    def list_organization_activity_log(self, conversation_id: str) -> List[ActivityLog]:
        """List organization activity log.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsActivitylog
        """
        return self.client.paginate(f"{self._url}/{conversation_id}/activitylog")

    def list_rating(self, conversation_id: str) -> List[ConversationRating]:
        """List rating.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsConversationidRating
        """
        return self.client.paginate(f"{self._url}/{conversation_id}/rating")

    def list_tags(self, conversation_id: str) -> List[Tag]:
        """List tags.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getConversationsConversationidTags
        """
        return self.client.paginate(f"{self._url}/{conversation_id}/tags")

    def patch_conversation_custom_attributes(
        self, conversation_id: str, body: ConversationPatchCustomAttributesBody
    ) -> List[ConversationCustomAttribute]:
        """Patch conversation custom attributes.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/patchConversationsConversationidCustom-attributes
        """
        data = self.client.patch(
            f"{self._url}/{conversation_id}/custom-attributes", body
        )
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        return [ConversationCustomAttribute(**item) for item in data]

    def reopen(self, conversation_id: str, body: ConversationReopenBody):
        """Reopen a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/putConversationsConversationidReopen
        """
        return self.client.put(f"{self._url}/{conversation_id}/reopen", body)

    def search(self, query: ConversationSearchQuery) -> List[ConversationSearchHit]:
        """Search conversations.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/getSearchConversations
        """
        return self.client.paginate(f"{self.base_url}/search/{self.resource}", query)

    def tag(self, conversation_id: str, tag_id: str):
        """Tag a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/putConversationsConversationidTagsTagid
        """
        return self.client.put(f"{self._url}/{conversation_id}/tags/{tag_id}")

    def untag(self, conversation_id: str, tag_id: str):
        """Untag a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/deleteConversationsConversationidTagsTagid
        """
        return self.client.delete(f"{self._url}/{conversation_id}/tags/{tag_id}")

    def transfer(self, conversation_id: str, body: ConversationTransferBody):
        """Transfer a conversation.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Conversations/#tag/Conversations/operation/putConversationsConversationidTransferQueue
        """
        return self.client.post(f"{self._url}/{conversation_id}/transfer/queue", body)
