from typing import List, Literal, TypedDict, Union

from .bulk_action import BulkActionFailure


class EndUserCustomAttribute(TypedDict):
    id: str
    identifier: str
    name: str
    value: List[str]


class _EndUserRequired(TypedDict):
    createdAt: str
    id: str


class _EndUserOptional(TypedDict, total=False):
    additionalEmails: List[str]
    additionalPhoneNumbers: List[str]
    avatarUrl: str
    customAttributes: List[EndUserCustomAttribute]
    displayName: str
    email: str
    externalId: str
    firstName: str
    lastName: str
    middleNames: List[str]
    phoneNumber: str


class EndUser(_EndUserRequired, _EndUserOptional):
    pass


class EndUserPatchBulkActionSuccess(TypedDict):
    data: EndUser
    _type: Literal["BulkActionSuccess"]


EndUserPatchBulkActionOutcome = Union[EndUserPatchBulkActionSuccess, BulkActionFailure]

EndUserPatchBulkActionOutcomes = [EndUserPatchBulkActionSuccess, BulkActionFailure]
