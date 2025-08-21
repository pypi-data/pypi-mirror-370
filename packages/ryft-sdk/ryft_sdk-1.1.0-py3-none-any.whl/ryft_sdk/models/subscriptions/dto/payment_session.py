from typing_extensions import List, NotRequired, TypedDict

from ryft_sdk.models.address import Address
from ryft_sdk.models.shipping_details import ShippingDetails


class CustomerDetails(TypedDict):
    id: NotRequired[str]
    firstName: NotRequired[str]
    lastName: NotRequired[str]
    homePhoneNumber: NotRequired[str]
    mobilePhoneNumber: NotRequired[str]
    metadata: NotRequired[dict[str, str]]


class CredentialsOnFileUsage(TypedDict):
    initiator: str
    sequence: str


class PreviousPayment(TypedDict):
    id: str


class RebillingDetail(TypedDict):
    amountVariance: str
    numberOfDaysBetweenPayments: int
    totalNumberOfPayments: NotRequired[int]
    currentPaymentNumber: NotRequired[int]
    expiry: NotRequired[int]


class TokenizedDetails(TypedDict):
    id: str
    stored: bool


class Card(TypedDict):
    scheme: str
    last4: str


class Wallet(TypedDict):
    type: str


class Checks(TypedDict):
    avsResponseCode: NotRequired[str]
    cvvResponseCode: NotRequired[str]


class SessionPaymentMethod(TypedDict):
    type: str
    tokenizedDetails: NotRequired[TokenizedDetails]
    card: NotRequired[Card]
    wallet: NotRequired[Wallet]
    billingAddress: NotRequired[Address]
    checks: NotRequired[Checks]


class Fee(TypedDict):
    amount: int


class SplitPaymentDetailItem(TypedDict):
    id: str
    accountId: str
    amount: int
    fee: Fee
    description: str
    metadata: NotRequired[dict[str, str]]


class SplitPaymentDetail(TypedDict):
    items: List[SplitPaymentDetailItem]


class StatementDescriptor(TypedDict):
    descriptor: str
    city: str


class RequiredAction(TypedDict):
    type: str
    url: str


class OrderDetailsItem(TypedDict):
    reference: str
    name: str
    quantity: int
    unitPrice: int
    taxAmount: int
    totalAmount: int
    discountAmount: int
    productUrl: str
    imageUrl: str


class OrderDetails(TypedDict):
    items: List[OrderDetailsItem]


class PaymentMethodOptions(TypedDict):
    disabled: List[str]


class PaymentSettings(TypedDict):
    paymentMethodOptions: PaymentMethodOptions


class PaymentSession(TypedDict):
    id: str
    amount: int
    currency: str
    paymentType: NotRequired[str]
    entryMode: NotRequired[str]
    customerEmail: NotRequired[str]
    customerDetails: NotRequired[CustomerDetails]
    credentialOnFileUsage: NotRequired[CredentialsOnFileUsage]
    previousPayment: NotRequired[PreviousPayment]
    rebillingDetail: NotRequired[RebillingDetail]
    enabledPaymentMethods: List[str]
    paymentMethod: NotRequired[SessionPaymentMethod]
    platformFee: NotRequired[int]
    splitPaymentDetail: SplitPaymentDetail
    status: str
    metadata: NotRequired[dict[str, str]]
    clientSecret: str
    lastError: NotRequired[str]
    refundedAmount: int
    statementDescriptor: StatementDescriptor
    requiredAction: NotRequired[RequiredAction]
    returnUrl: str
    authorizationType: NotRequired[str]
    captureFlow: NotRequired[str]
    verifyAccount: NotRequired[bool]
    shippingDetails: NotRequired[ShippingDetails]
    orderDetails: NotRequired[OrderDetails]
    paymentSettings: NotRequired[PaymentSettings]
    createdTimestamp: int
    lastUpdatedTimestamp: int


class PaymentSessions(TypedDict):
    items: List[PaymentSession]
    paginationToken: NotRequired[str]
