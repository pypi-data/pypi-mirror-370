from typing_extensions import List, NotRequired, TypedDict

from ryft_sdk.models.address import Address


class Card(TypedDict):
    scheme: str
    last4: str
    expiryMonth: str
    expiryYear: str


class Checks(TypedDict):
    avsResponseCode: NotRequired[str]
    cvvResponseCode: NotRequired[str]


class PaymentMethod(TypedDict):
    id: str
    type: str
    customerId: NotRequired[str]
    createdTimestamp: int
    card: NotRequired[Card]
    billingAddress: NotRequired[Address]
    checks: NotRequired[Checks]


class PaymentMethods(TypedDict):
    items: List[PaymentMethod]
