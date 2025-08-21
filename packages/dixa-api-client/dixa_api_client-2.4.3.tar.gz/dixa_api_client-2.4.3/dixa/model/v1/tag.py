from typing import Literal, TypedDict

TagState = Literal["Active", "Inactive"]


class _TagRequired(TypedDict):
    id: str
    name: str
    state: TagState


class _TagOptional(TypedDict, total=False):
    color: str


class Tag(_TagRequired, _TagOptional):
    pass
