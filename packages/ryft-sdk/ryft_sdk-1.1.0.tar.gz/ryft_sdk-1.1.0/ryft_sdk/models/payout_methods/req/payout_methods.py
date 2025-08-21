from typing_extensions import NotRequired, TypedDict
from ryft_sdk.models.address import Address


class BankAccountRequest(TypedDict):
    bankIdType: NotRequired[str]
    bankId: NotRequired[str]
    accountNumberType: str
    accountNumber: str
    address: NotRequired[Address]


class CreatePayoutMethodRequest(TypedDict):
    type: str
    displayName: NotRequired[str]
    currency: str
    country: str
    bankAccount: BankAccountRequest


class UpdatePayoutMethodRequest(TypedDict):
    displayName: NotRequired[str]
    bankAccount: NotRequired[BankAccountRequest]
