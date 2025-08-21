from typing import List, Literal, TypedDict, Union

from .bulk_action import BulkActionFailure


class _AgentRequired(TypedDict):
    createdAt: str
    displayName: str
    email: str
    id: str


class _AgentOptional(TypedDict, total=False):
    additionalEmails: List[str]
    additionalPhoneNumbers: List[str]
    avatarUrl: str
    firstName: str
    lastName: str
    middleNames: List[str]
    phoneNumber: str
    roles: List[str]


class Agent(_AgentRequired, _AgentOptional):
    pass


ConnectionStatus = Literal["Online", "Offline"]

PresenceStatus = Literal["Away", "Working"]


class _AgentPresenceRequired(TypedDict):
    connectionStatus: ConnectionStatus
    requestTime: str
    userId: str


class _AgentPresenceOptional(TypedDict, total=False):
    activeChannels: List[str]
    lastSeen: str
    presenceStatus: PresenceStatus


class AgentPresence(_AgentPresenceRequired, _AgentPresenceOptional):
    pass


class AgentBulkActionSuccess(TypedDict):
    data: List[Agent]
    _type: Literal["BulkActionSuccess"]


AgentBulkActionOutcome = Union[AgentBulkActionSuccess, BulkActionFailure]


AgentBulkActionOutcomes = [AgentBulkActionSuccess, BulkActionFailure]
