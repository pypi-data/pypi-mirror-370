from typing import Literal, Optional, TypedDict, Union


class EmptyPatchSet(TypedDict):
    id: str
    message: str
    _type: Literal["EmptyPatchSet"]


class ErrorResponse(TypedDict):
    message: str
    _type: Literal["ErrorResponse"]


class Infrastructure(TypedDict):
    id: str
    message: str
    _type: Literal["Infrastructure"]


class Integrity(TypedDict):
    id: str
    message: str
    _type: Literal["Integrity"]


class NotFound(TypedDict):
    id: str
    message: str
    _type: Literal["NotFound"]


class Validation(TypedDict):
    id: Optional[str]
    message: str
    _type: Literal["Validation"]


BulkActionFailureError = Union[
    EmptyPatchSet, ErrorResponse, Infrastructure, Integrity, NotFound, Validation
]


class BulkActionFailure(TypedDict):
    error: BulkActionFailureError
    _type: Literal["BulkActionFailure"]
