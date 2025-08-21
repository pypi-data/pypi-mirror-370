from typing_extensions import NotRequired, TypedDict


class TransferDestinationRequest(TypedDict):
    accountId: str


class CreateTransferRequest(TypedDict):
    amount: int
    currency: str
    source: NotRequired[TransferDestinationRequest]
    destination: NotRequired[TransferDestinationRequest]
    reason: NotRequired[str]
    metadata: NotRequired[dict[str, str]]
