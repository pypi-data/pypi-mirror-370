from typing import TypedDict


class CreateTmpLinkReq(TypedDict):
    url: str
    createdTimestamp: int
    expiresTimestamp: int
