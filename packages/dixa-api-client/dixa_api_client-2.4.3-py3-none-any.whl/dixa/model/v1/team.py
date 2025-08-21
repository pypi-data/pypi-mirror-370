from typing import TypedDict


class Team(TypedDict):
    id: str


class Team1(TypedDict):
    id: str
    name: str


class _TeamMemberRequired(TypedDict):
    id: str


class _TeamMemberOptional(TypedDict, total=False):
    email: str
    name: str
    phoneNumber: str


class TeamMember(_TeamMemberRequired, _TeamMemberOptional):
    pass
