from typing_extensions import List, NotRequired, TypedDict


class PlatformFee(TypedDict):
    id: str
    paymentSessionId: str
    amount: int
    paymentAmount: int
    netAmount: int
    currency: str
    fromAccountId: str
    createdTimestamp: int


class PlatformFees(TypedDict):
    items: List[PlatformFee]


class PlatformFeeRefund(TypedDict):
    id: str
    platformFeeId: str
    amount: int
    currency: str
    reason: NotRequired[str]
    status: str
    createdTimestamp: int
    lastUpdatedTimestamp: int


class PlatformFeeRefunds(TypedDict):
    items: List[PlatformFeeRefund]
