from typing_extensions import List, NotRequired, TypedDict

from ryft_sdk.models.address import Address
from ryft_sdk.models.shipping_details import ShippingDetails


class CustomerDetailsRequest(TypedDict):
    id: NotRequired[str]
    firstName: NotRequired[str]
    lastName: NotRequired[str]
    homePhoneNumber: NotRequired[str]
    mobilePhoneNumber: NotRequired[str]
    metadata: NotRequired[dict[str, str]]


class FeeRequest(TypedDict):
    amount: int


class SplitPaymentRequest(TypedDict):
    id: NotRequired[str]
    accountId: NotRequired[str]
    amount: NotRequired[int]
    description: NotRequired[str]
    fee: NotRequired[FeeRequest]
    metadata: NotRequired[dict[str, str]]


class SplitPaymentsRequest(TypedDict):
    items: List[SplitPaymentRequest]


class PreviousPaymentRequest(TypedDict):
    id: str


class RebillingDetailsRequest(TypedDict):
    amountVeriance: NotRequired[str]
    numberOfDaysBetweenPayments: int
    totalNumberOfPayments: NotRequired[int]
    currentPaymentNumber: NotRequired[int]
    expiry: NotRequired[int]


class OrderDetailRequest(TypedDict):
    reference: str
    name: str
    quantity: int
    unitPrice: int
    taxAmount: int
    totalAmount: int
    discountAmount: NotRequired[int]
    productUrl: NotRequired[str]
    imageUrl: NotRequired[str]


class OrderDetailsRequest(TypedDict):
    items: List[OrderDetailRequest]


class StatementDescriptorRequest(TypedDict):
    descriptor: str
    city: str


class PaymentMethodRequest(TypedDict):
    id: str
    cvc: NotRequired[str]


class CreatePaymentSessionAttemptPaymentRequest(TypedDict):
    paymentMethod: PaymentMethodRequest


class Ts2Py_gdB5O4Lcvi(TypedDict):
    disabled: List[str]


class PaymentSettingsRequest(TypedDict):
    paymentMethodOptions: Ts2Py_gdB5O4Lcvi


class CreatePaymentSessionRequest(TypedDict):
    amount: int
    currency: str
    customerEmail: NotRequired[str]
    customerDetails: NotRequired[CustomerDetailsRequest]
    platformFeee: NotRequired[int]
    splits: NotRequired[SplitPaymentsRequest]
    captureFlow: NotRequired[str]
    paymentType: str
    entryMode: NotRequired[str]
    previousPayment: NotRequired[PreviousPaymentRequest]
    rebillingDetail: NotRequired[RebillingDetailsRequest]
    verifyAccount: NotRequired[bool]
    shippingDetails: NotRequired[ShippingDetails]
    orderDetails: NotRequired[OrderDetailsRequest]
    statementDescriptor: NotRequired[StatementDescriptorRequest]
    metadata: NotRequired[dict[str, str]]
    returnUrl: NotRequired[str]
    attemptPayment: NotRequired[CreatePaymentSessionAttemptPaymentRequest]
    paymentSettings: NotRequired[PaymentSettingsRequest]


class UpdatePaymentSessionRequest(TypedDict):
    amount: NotRequired[int]
    customerEmail: NotRequired[str]
    platformFee: NotRequired[int]
    splits: NotRequired[SplitPaymentsRequest]
    metadata: NotRequired[dict[str, str]]
    captureFlow: NotRequired[str]
    shippingDetails: NotRequired[ShippingDetails]
    orderDetails: NotRequired[OrderDetailsRequest]
    paymentSettings: NotRequired[PaymentSettingsRequest]


class CardDetailsRequest(TypedDict):
    number: str
    expiryMonth: str
    expiryYear: str
    cvc: NotRequired[str]
    name: NotRequired[str]


class WalletDetailsRequest(TypedDict):
    type: str
    googlePayToken: NotRequired[str]
    applePayToken: NotRequired[str]


class PaymentMethodOptionsRequest(TypedDict):
    store: bool


class BrowserDetailsRequest(TypedDict):
    acceptHeader: str
    colorDepth: int
    javaEnabled: bool
    language: str
    screenHeight: int
    screenWidth: int
    timeZoneOffset: int
    userAgent: str


class ThreeDsRequestDetails(TypedDict):
    deviceChannel: str
    browserDetails: NotRequired[BrowserDetailsRequest]


class AttemptPaymentSessionRequest(TypedDict):
    clientSecret: str
    paymentMethodType: NotRequired[str]
    cardDetails: NotRequired[CardDetailsRequest]
    walletDetails: NotRequired[WalletDetailsRequest]
    paymentMethod: NotRequired[PaymentMethodRequest]
    paymentMethodOptions: NotRequired[PaymentMethodOptionsRequest]
    billingAddress: NotRequired[Address]
    customerDetails: NotRequired[CustomerDetailsRequest]
    threeDsRequestDetails: NotRequired[ThreeDsRequestDetails]


class ThreeDsRequest(TypedDict):
    fingerprint: NotRequired[str]
    challengeResult: NotRequired[str]


class ContinuePaymentSessionRequest(TypedDict):
    clientSecret: str
    threeDs: ThreeDsRequest
