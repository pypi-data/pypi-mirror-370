from typing_extensions import List, NotRequired, TypedDict
from ryft_sdk.models.address import Address


class BankAccount(TypedDict):
    bankIdType: str
    bankId: NotRequired[str]
    accountNumberType: str
    accountNumber: str
    address: NotRequired[Address]


class PayoutMethod(TypedDict):
    id: str
    type: str
    displayName: NotRequired[str]
    currency: str
    countryCode: str
    bankAccount: BankAccount
    createdTimestamp: int
    lastUpdatedTimestamp: int


class PayoutMethods(TypedDict):
    items: List[PayoutMethod]
    paginationToken: NotRequired[str]
