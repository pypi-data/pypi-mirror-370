from typing import Dict, List, Literal, TypedDict, Union


class _QueueRequired(TypedDict):
    id: str


class _QueueOptional(TypedDict, total=False):
    queuedAt: str


class Queue(_QueueRequired, _QueueOptional):
    pass


Channel = Literal[
    "WhatsApp",
    "Voicemail",
    "WidgetChat",
    "FacebookMessenger",
    "Email",
    "PstnPhone",
    "Sms",
    "Twitter",
    "Chat",
    "Messenger",
]

RatingStatus = Literal["Unscheduled", "Offered", "Rated", "Scheduled", "Cancelled"]

RatingType = Literal["CSAT", "ThumbsUpOrDown"]


class _ConversationRatingRequired(TypedDict):
    conversationChannel: Channel
    id: str
    ratingStatus: RatingStatus
    ratingType: RatingType
    timestamps: Dict[str, str]
    userId: str


class _ConversationRatingOptional(TypedDict, total=False):
    agentId: str
    language: str
    ratingCommend: str
    ratingScore: int


class ConversationRating(_ConversationRatingRequired, _ConversationRatingOptional):
    pass


class ConversationFlow(TypedDict):
    channel: Channel
    contactEndpointId: str
    id: str
    name: str


class ConversationCustomAttribute(TypedDict):
    id: str
    identifier: str
    name: str
    value: Union[str, List[str]]


class EmailForward(TypedDict):
    _type: Literal["EmailForward"]
    parentId: str


class FollowUp(TypedDict):
    _type: Literal["FollowUp"]
    parentId: str


class SideConversation(TypedDict):
    _type: Literal["SideConversation"]
    parentId: str


ConversationLink = Union[EmailForward, FollowUp, SideConversation]

ConversationState = Literal["AwaitingPending", "Pending", "Closed", "Open"]


class _AnonymizedConversationRequired(TypedDict):
    anonymizedAt: str
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _AnonymizedConversationOptional(TypedDict, total=False):
    customAttributes: List[ConversationCustomAttribute]
    link: ConversationLink
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["AnonymizedConversation"]


class AnonymizedConversation(
    _AnonymizedConversationRequired, _AnonymizedConversationOptional
):
    pass


class Assignment(TypedDict):
    agentId: str
    assignedAt: str


class _BrowserInfoRequired(TypedDict):
    name: str


class _BrowserInfoOptional(TypedDict, total=False):
    ipAddress: str
    originatingUrl: str
    version: str


class BrowserInfo(_BrowserInfoRequired, _BrowserInfoOptional):
    pass


Direction = Literal["Inbound", "Outbound"]


class _ChatConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _ChatConversationOptional(TypedDict, total=False):
    assignment: Assignment
    browserInfo: BrowserInfo
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    language: str
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["ChatConversation"]


class ChatConversation(_ChatConversationRequired, _ChatConversationOptional):
    pass


class _ContactFormConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    fromEmail: str
    id: str
    requesterId: str


class _ContactFormConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    integrationEmail: str
    language: str
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    subject: str
    toEmail: str
    _type: Literal["ContactFormConversation"]


class ContactFormConversation(
    _ContactFormConversationRequired, _ContactFormConversationOptional
):
    pass


class _EmailConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    fromEmail: str
    id: str
    requesterId: str
    toEmail: str


class _EmailConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    integrationEmail: str
    language: str
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    subject: str
    _type: Literal["EmailConversation"]


class EmailConversation(_EmailConversationRequired, _EmailConversationOptional):
    pass


class _FacebookMessengerConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _FacebookMessengerConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["FacebookMessengerConversation"]


class FacebookMessengerConversation(
    _FacebookMessengerConversationRequired, _FacebookMessengerConversationOptional
):
    pass


class _GenericConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _GenericConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    fromContactPointId: str
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    toContactPointId: str
    _type: Literal["GenericConversation"]


class GenericConversation(_GenericConversationRequired, _GenericConversationOptional):
    pass


class _MessengerConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _MessengerConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    language: str
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["MessengerConversation"]


class MessengerConversation(
    _MessengerConversationRequired, _MessengerConversationOptional
):
    pass


class _PstnPhoneConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _PstnPhoneConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["PstnPhoneConversation"]


class PstnPhoneConversation(
    _PstnPhoneConversationRequired, _PstnPhoneConversationOptional
):
    pass


class _SmsConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _SmsConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    fromNumber: str
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    toNumber: str
    _type: Literal["SmsConversation"]


class SmsConversation(_SmsConversationRequired, _SmsConversationOptional):
    pass


ConversationType = Literal["DirectMessage", "Tweet"]


class _TwitterConversationRequired(TypedDict):
    channel: Channel
    conversationType: ConversationType
    createdAt: str
    id: str
    requesterId: str


class _TwitterConversationOptional(TypedDict, total=False):
    assignment: Assignment
    contactPointTwitterId: str
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    endUserTwitterId: str
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["TwitterConversation"]


class TwitterConversation(_TwitterConversationRequired, _TwitterConversationOptional):
    pass


class _WhatsAppConversationRequired(TypedDict):
    channel: Channel
    createdAt: str
    id: str
    requesterId: str


class _WhatsAppConversationOptional(TypedDict, total=False):
    assignment: Assignment
    customAttributes: List[ConversationCustomAttribute]
    direction: Direction
    link: ConversationLink
    queue: Queue
    state: ConversationState
    stateUpdatedAt: str
    _type: Literal["WhatsAppConversation"]


class WhatsAppConversation(
    _WhatsAppConversationRequired, _WhatsAppConversationOptional
):
    pass


class _ConversationSearchInnerHitRequired(TypedDict):
    id: str


class _ConversationSearchInnerHitOptional(TypedDict, total=False):
    highlights: Dict[str, List[str]]


class ConversationSearchInnerHit(
    _ConversationSearchInnerHitRequired, _ConversationSearchInnerHitOptional
):
    pass


class _ConversationSearchHitRequired(TypedDict):
    id: str


class _ConversationSearchHitOptional(TypedDict, total=False):
    highlights: Dict[str, List[str]]
    innerHits: List[ConversationSearchInnerHit]


class ConversationSearchHit(
    _ConversationSearchHitRequired, _ConversationSearchHitOptional
):
    pass


Conversation = Union[
    AnonymizedConversation,
    ChatConversation,
    ContactFormConversation,
    EmailConversation,
    FacebookMessengerConversation,
    GenericConversation,
    MessengerConversation,
    PstnPhoneConversation,
    SmsConversation,
    TwitterConversation,
    WhatsAppConversation,
]


ConversationTypes = [
    AnonymizedConversation,
    ChatConversation,
    ContactFormConversation,
    EmailConversation,
    FacebookMessengerConversation,
    GenericConversation,
    MessengerConversation,
    PstnPhoneConversation,
    SmsConversation,
    TwitterConversation,
    WhatsAppConversation,
]


class ConversationResponse(TypedDict):
    id: int
