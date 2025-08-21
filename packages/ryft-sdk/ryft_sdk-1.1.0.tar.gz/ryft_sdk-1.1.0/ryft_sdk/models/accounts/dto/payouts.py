from typing_extensions import List, NotRequired, TypedDict


class PayoutBankAccount(TypedDict):
    bankIdType: NotRequired[str]
    bankId: NotRequired[str]
    bankName: NotRequired[str]
    accountNumberType: str
    last4: str


class PayoutMethod(TypedDict):
    id: str
    bankAccount: PayoutBankAccount


class Payout(TypedDict):
    id: str
    paymentsTakeDateFrom: str
    paymentsTakeDateTo: str
    amount: int
    currency: str
    status: str
    scheduleType: str
    payoutMethod: NotRequired[PayoutMethod]
    failureReason: NotRequired[str]
    scheme: NotRequired[str]
    createdTimestamp: int
    scheduledTimestamp: int
    completedTimestamp: NotRequired[int]
    metadata: NotRequired[dict[str, str]]


class Payouts(TypedDict):
    payouts: List[Payout]
    paginationToken: NotRequired[str]
