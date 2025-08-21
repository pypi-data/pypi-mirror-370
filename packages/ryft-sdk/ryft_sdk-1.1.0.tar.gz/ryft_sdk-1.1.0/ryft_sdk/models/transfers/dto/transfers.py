from typing_extensions import List, NotRequired, TypedDict


class TransferDestination(TypedDict):
    accountId: str


class TransferError(TypedDict):
    code: str
    description: str


class Transfer(TypedDict):
    id: str
    status: str
    amount: int
    currency: str
    reason: NotRequired[str]
    source: NotRequired[TransferDestination]
    destination: NotRequired[TransferDestination]
    errors: NotRequired[List[TransferError]]
    metadata: NotRequired[dict[str, str]]
    createdTimestamp: int
    lastUpdatedTimestamp: int


class Transfers(TypedDict):
    items: List[Transfer]
    paginationToken: NotRequired[str]
