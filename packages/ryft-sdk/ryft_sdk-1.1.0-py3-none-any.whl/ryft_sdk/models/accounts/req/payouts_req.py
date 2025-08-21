from typing_extensions import NotRequired, TypedDict


class CreatePayoutRequest(TypedDict):
    amount: int
    currency: str
    payoutMethodId: str
    metadata: NotRequired[dict[str, str]]
