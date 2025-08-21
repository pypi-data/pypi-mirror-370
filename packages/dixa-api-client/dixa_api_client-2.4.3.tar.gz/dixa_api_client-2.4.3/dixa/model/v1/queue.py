from typing import Dict, List, Literal, TypedDict, Union

from .bulk_action import BulkActionFailure
from .conversation import Channel


class _QueueRequired(TypedDict):
    id: str


class _QueueOptional(TypedDict, total=False):
    queuedAt: str


class Queue(_QueueRequired, _QueueOptional):
    pass


MemberListType = Literal["Default", "SkillBased"]

OfferingAlgorithm = Literal[
    "AgentPriorityOneAtATimeRandom",
    "AllAtOnce",
    "AgentPriorityLongestIdle",
    "AgentPriorityAllAtOnce",
    "LongestIdle",
    "OneAtATimeRandom",
]

QueueThreshold = Literal[
    "SlaTimeLimit",
    "AvailableAgents",
    "LongestWait",
    "SlaPercentage",
    "WaitingConversations",
]

SLACalculationMethod = Literal["AbandonedIgnored"]


class QueueUsages(TypedDict):
    queueId: str
    usages: Dict[Channel, List[str]]


class _Queue1Required(TypedDict):
    doNotOfferTimeouts: Dict[Channel, int]
    id: str
    isDefault: bool
    isDoNotOfferEnabled: bool
    name: str
    organizationId: str


class _Queue1Optional(TypedDict, total=False):
    isPreferredAgentEnabled: bool
    memberListType: MemberListType
    offerAbandonedConversations: bool
    offeringAlgorithm: OfferingAlgorithm
    offerTimeout: int
    personalAgentOfflineTimeout: int
    preferredAgentOfflineTimeout: int
    preferredAgentTimeouts: Dict[Channel, int]
    priority: int
    queueThresholds: Dict[QueueThreshold, int]
    slaCalculationMethod: SLACalculationMethod
    usages: QueueUsages
    wrapupTimeout: int


class Queue1(_Queue1Required, _Queue1Optional):
    pass


class AssignAgentBulkActionSuccess(TypedDict):
    data: str
    _type: Literal["BulkActionSuccess"]


AssignAgentOutcome = Union[BulkActionFailure, AssignAgentBulkActionSuccess]

AssignAgentOutcomes = [BulkActionFailure, AssignAgentBulkActionSuccess]


class _QueueMemberRequired(TypedDict):
    agentId: str


class _QueueMemberOptional(TypedDict, total=False):
    priority: int


class QueueMember(_QueueMemberRequired, _QueueMemberOptional):
    pass
