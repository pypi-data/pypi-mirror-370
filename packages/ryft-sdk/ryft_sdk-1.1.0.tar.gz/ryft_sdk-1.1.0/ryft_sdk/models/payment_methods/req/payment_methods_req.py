from typing_extensions import TypedDict
from ryft_sdk.models.address import Address


class UpdatePaymentMethodRequest(TypedDict):
    billingAddress: Address
