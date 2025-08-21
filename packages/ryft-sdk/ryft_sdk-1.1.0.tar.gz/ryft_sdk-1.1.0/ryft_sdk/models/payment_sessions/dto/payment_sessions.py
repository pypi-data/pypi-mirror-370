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


class PaymentSessionCredentialOnFileUsage(TypedDict):
    initiator: str
    sequence: str


class PaymentSessionPreviousPayment(TypedDict):
    id: str


class RebillingDetail(TypedDict):
    amountVariance: str
    numberOfDaysBetweenPayments: int
    totalNumberOfPayments: NotRequired[int]
    currentPaymentNumber: NotRequired[int]
    expiry: NotRequired[int]


class PaymentSessionTokenizedDetails(TypedDict):
    id: str
    stored: bool


class PaymentSessionCard(TypedDict):
    scheme: str
    last4: str


class PaymentSessionWallet(TypedDict):
    type: str


class PaymentSessionChecks(TypedDict):
    avsResponseCode: NotRequired[str]
    cvvResponseCode: NotRequired[str]


class PaymentSessionPaymentMethod(TypedDict):
    type: str
    tokenizedDetails: NotRequired[PaymentSessionTokenizedDetails]
    card: NotRequired[PaymentSessionCard]
    wallet: PaymentSessionWallet
    billingAddress: NotRequired[Address]
    checks: NotRequired[PaymentSessionChecks]


class PaymentSessionFee(TypedDict):
    amount: int


class SplitPaymentDetail(TypedDict):
    id: str
    accountId: str
    amount: int
    fee: NotRequired[PaymentSessionFee]
    description: str
    metadata: NotRequired[dict[str, str]]


class SplitPaymentDetails(TypedDict):
    items: List[SplitPaymentDetail]


class StatementDescriptor(TypedDict):
    descriptor: str
    city: str


class Identify(TypedDict):
    uniqueId: NotRequired[str]
    threeDsMethodUrl: str
    threeDsMethodSignature: str
    sessionId: str
    sessionSecret: str
    threeDsMethodData: str
    scheme: str
    paymentMethodId: str


class RequiredAction(TypedDict):
    type: str
    url: NotRequired[str]
    identify: Identify


class OrderDetail(TypedDict):
    reference: str
    name: str
    quantity: int
    unitPrice: int
    taxAmount: int
    totalAmount: int
    discountAmount: int
    productUrl: NotRequired[str]
    imageUrl: NotRequired[str]


class OrderDetails(TypedDict):
    items: List[OrderDetail]


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
    credentialOnFileUsage: NotRequired[PaymentSessionCredentialOnFileUsage]
    previousPayment: NotRequired[PaymentSessionPreviousPayment]
    rebillingDetail: NotRequired[RebillingDetail]
    enabledPaymentMethods: List[str]
    paymentMethod: NotRequired[PaymentSessionPaymentMethod]
    platformFee: NotRequired[int]
    splitPaymentDetail: SplitPaymentDetails
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
