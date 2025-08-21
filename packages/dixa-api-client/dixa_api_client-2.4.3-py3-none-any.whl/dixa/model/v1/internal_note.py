from typing import TypedDict


class InternalNote(TypedDict):
    authorId: str
    createdAt: str
    csid: int
    id: str
    message: str
