from typing import Literal, Optional, TypedDict

AnonymizationRequestType = Literal["Conversation", "Message", "User"]


class AnonymizationRequest(TypedDict):
    _type: AnonymizationRequestType
    id: str
    initiatedAt: str
    processedAt: Optional[str]
    requestedBy: str
    targetEntityId: str
