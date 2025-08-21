from typing import List, Literal, TypedDict, Union

ActivityLogType = Literal[
    "ConversationRatingScheduled",
    "ConversationOfferAccepted",
    "ConversationPending",
    "ConversationRatingUnscheduled",
    "ConversationOfferRejected",
    "ConversationEndUserReplaced",
    "NoteAdded",
    "FollowupExpired",
    "ConversationRated",
    "TagAdded",
    "ConversationOfferTimeout",
    "MessageAddedByCustomer",
    "ConversationCreatedByCustomer",
    "ConversationCreatedByAgent",
    "TransferFailed",
    "TransferSuccessful",
    "ConversationOffered",
    "ConversationUnassigned",
    "TagRemoved",
    "TransferInitiated",
    "ConversationClaimed",
    "ConversationReopened",
    "ConversationClosed",
    "ConversationLanguageUpdated",
    "FollowupAdded",
    "ConversationAutoreplySent",
    "ConversationReserved",
    "ConversationAssigned",
    "ConversationRatingOffered",
    "ConversationRatingCancelled",
    "MessageAddedByAgent",
    "FollowupRemoved",
]


class _ActivityLogUserRequired(TypedDict):
    id: str


class _ActivityLogUserOptional(TypedDict, total=False):
    email: str
    name: str
    phoneNumber: str


class ActivityLogUser(_ActivityLogUserRequired, _ActivityLogUserOptional):
    pass


class _ConversationAssignedAttributeRequired(TypedDict):
    agentId: str


class _ConversationAssignedAttributeOptional(TypedDict, total=False):
    agentName: str


class ConversationAssignedAttribute(
    _ConversationAssignedAttributeRequired, _ConversationAssignedAttributeOptional
):
    pass


class ConversationAutoReplySentAttribute(TypedDict):
    templateName: str


class ConversationClaimedAttribute(TypedDict, total=False):
    claimedFromLabel: str
    claimedFromType: str


class ConversationCreatedAttribute(TypedDict, total=False):
    subject: str


class ConversationEndUserReplacedAttribute(TypedDict):
    newUser: ActivityLogUser
    oldUser: ActivityLogUser


class ConversationLanguageUpdatedAttribute(TypedDict):
    language: str


class ConversationOfferedAttribute(TypedDict, total=False):
    agentNames: List[str]
    queueLabel: str


class _ConversationRatedAttributeRequired(TypedDict):
    agent: ActivityLogUser


class _ConversationRatedAttributeOptional(TypedDict, total=False):
    message: str
    score: int


class ConversationRatedAttribute(
    _ConversationRatedAttributeRequired, _ConversationRatedAttributeOptional
):
    pass


class ConversationRatingOfferedAttribute(TypedDict):
    agent: ActivityLogUser
    user: ActivityLogUser


class ConversationRatingScheduledAttribute(TypedDict):
    ratingScheduledTime: str


class ConversationReservedAttribute(TypedDict):
    agent: ActivityLogUser
    queueId: str
    queueName: str
    reservationType: str
    validUntil: str


class _ConversationTransferredAttributeRequired(TypedDict):
    destinationId: str
    destinationType: str
    transferType: str


class _ConversationTransferredAttributeOptional(TypedDict, total=False):
    destinationLabel: str
    reason: str


class ConversationTransferredAttribute(
    _ConversationTransferredAttributeRequired, _ConversationTransferredAttributeOptional
):
    pass


class ConversationUnassignedAttribute(TypedDict, total=False):
    agent: ActivityLogUser


class _MessageAddedAttributeRequired(TypedDict):
    messageId: str


class _MessageAddedAttributeOptional(TypedDict, total=False):
    avatarUrl: str
    fromEndpoint: str


class MessageAddedAttribute(
    _MessageAddedAttributeRequired, _MessageAddedAttributeOptional
):
    pass


class _NoteAddedAttributeRequired(TypedDict):
    messageId: str


class _NoteAddedAttributeOptional(TypedDict, total=False):
    avatarUrl: str


class NoteAddedAttribute(_NoteAddedAttributeRequired, _NoteAddedAttributeOptional):
    pass


class TagAddedAttribute(TypedDict):
    tag: str


class TagRemovedAttribute(TypedDict):
    tag: str


ActivityLogAttributes = Union[
    ConversationAssignedAttribute,
    ConversationAutoReplySentAttribute,
    ConversationClaimedAttribute,
    ConversationCreatedAttribute,
    ConversationEndUserReplacedAttribute,
    ConversationLanguageUpdatedAttribute,
    ConversationOfferedAttribute,
    ConversationRatedAttribute,
    ConversationRatingOfferedAttribute,
    ConversationRatingScheduledAttribute,
    ConversationReservedAttribute,
    ConversationTransferredAttribute,
    ConversationUnassignedAttribute,
    MessageAddedAttribute,
    NoteAddedAttribute,
    TagAddedAttribute,
    TagRemovedAttribute,
]


class _ActivityLogRequired(TypedDict):
    conversationId: str


class _ActivityLogOptional(TypedDict, total=False):
    _type: ActivityLogType
    activityTimestamp: str
    attributes: ActivityLogAttributes
    author: ActivityLogUser
    id: str


class ActivityLog(_ActivityLogRequired, _ActivityLogOptional):
    pass
