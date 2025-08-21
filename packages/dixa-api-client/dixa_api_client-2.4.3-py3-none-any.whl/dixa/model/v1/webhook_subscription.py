from typing import Dict, List, Literal, Optional, TypedDict, Union


class WebhookSubscription(TypedDict):
    createdAt: str
    createdBy: str
    enabled: bool
    headers: Dict[str, str]
    id: str
    name: str
    secretKey: str
    subscribedEvents: Optional[List[str]]
    updatedAt: str
    updatedBy: str
    url: str


class DeliveryDetail(TypedDict):
    deliveryTimestamp: str
    responseCode: int
    responseText: str
    success: bool
    _type: Literal["DeliveryDetail"]


class NoRecentDelivery(TypedDict):
    _type: Literal["NoRecentDelivery"]


class EventDeliveryLog(TypedDict):
    deliveryDetail: DeliveryDetail
    payload: str


DeliveryStatus = Union[DeliveryDetail, NoRecentDelivery]

Event = Literal[
    "ConversationPending",
    "AgentUnbannedEnduser",
    "ConversationMessageAdded",
    "ConversationTagAdded",
    "AgentBannedIp",
    "ConversationAssigned",
    "ConversationPendingExpired",
    "ConversationTransferred",
    "ConversationEnqueued",
    "ConversationCreated",
    "ConversationUnassigned",
    "ConversationOpen",
    "ConversationAbandoned",
    "ConversationClosed",
    "ConversationNoteAdded",
    "AgentBannedEnduser",
    "ConversationEndUserReplaced",
    "AgentUnbannedIp",
    "ConversationTagRemoved",
    "ConversationRated",
]


class EventDeliveryStatus(TypedDict):
    deliveryStatus: DeliveryStatus
    event: Event


class BasicAuth(TypedDict):
    password: str
    username: str
    _type: Literal["BasicAuth"]


class NoAuth(TypedDict):
    _type: Literal["NoAuth"]


class TokenAuth(TypedDict):
    value: str
    _type: Literal["TokenAuth"]


Authorization = Union[BasicAuth, NoAuth, TokenAuth]
