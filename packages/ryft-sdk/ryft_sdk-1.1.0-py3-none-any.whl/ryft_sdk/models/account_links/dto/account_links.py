from typing_extensions import TypedDict


class TemporaryAccountLink(TypedDict):
    url: str
    createdTimestamp: int
    expiresTimestamp: int
