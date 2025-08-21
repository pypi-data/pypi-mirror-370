from typing import List, TypedDict, Union


class _EmailEndpointRequired(TypedDict):
    address: str


class _EmailEndpointOptional(TypedDict, total=False):
    name: str
    senderOverride: str


class EmailEndpoint(_EmailEndpointRequired, _EmailEndpointOptional):
    pass


class _TelephonyEndpointRequired(TypedDict):
    number: str


class _TelephonyEndpointOptional(TypedDict, total=False):
    functionality: List[str]
    name: str


class TelephonyEndpoint(_TelephonyEndpointRequired, _TelephonyEndpointOptional):
    pass


ContactEndpoint = Union[EmailEndpoint, TelephonyEndpoint]

ContactEndpoints = [EmailEndpoint, TelephonyEndpoint]
