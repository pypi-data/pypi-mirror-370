from typing_extensions import List, NotRequired, TypedDict
from ryft_sdk.models.payment_sessions.dto.payment_sessions import RequiredAction
from ryft_sdk.models.shipping_details import ShippingDetails


class SubscriptionCustomer(TypedDict):
    id: str


class SubscriptionPaymentSession(TypedDict):
    id: str
    clientSecret: NotRequired[str]
    requiredActions: NotRequired[RequiredAction]


class SubscriptionPaymentSessions(TypedDict):
    initial: SubscriptionPaymentSession
    latest: SubscriptionPaymentSession


class SubscriptionInterval(TypedDict):
    unit: str
    times: NotRequired[int]


class RecurringPrice(TypedDict):
    amount: int
    currency: str
    interval: SubscriptionInterval


class SubscriptionBalance(TypedDict):
    amount: int


class SubscriptionPausePaymentDetail(TypedDict):
    reason: NotRequired[str]
    resumeAtTimestamp: NotRequired[int]
    pausedAtTimestamp: int


class SubscriptionCancelDetail(TypedDict):
    reason: NotRequired[str]
    cancelledAtTimestamp: int


class SubscriptionFailureDetail(TypedDict):
    paymentAttempts: int
    lastPaymentError: str


class SubscriptionBillingDetail(TypedDict):
    totalCycles: int
    currentCycle: int
    currentCycleStartTimestamp: int
    currentCycleEndTimestamp: int
    billingCycleTimestamp: int
    nextBillingTimestamp: NotRequired[int]
    failureDetail: NotRequired[SubscriptionFailureDetail]


class StatementDescriptor(TypedDict):
    descriptor: str
    city: str


class SubscriptionPaymentSettings(TypedDict):
    statementDescriptor: NotRequired[StatementDescriptor]


class Subscription(TypedDict):
    id: str
    status: str
    description: NotRequired[str]
    customer: SubscriptionCustomer
    paymentMethod: SubscriptionCustomer
    paymentSessions: SubscriptionPaymentSessions
    price: RecurringPrice
    balance: SubscriptionBalance
    pausePaymentDetail: NotRequired[SubscriptionPausePaymentDetail]
    cancelDetail: NotRequired[SubscriptionCancelDetail]
    billingDetail: SubscriptionBillingDetail
    shippingDetails: NotRequired[ShippingDetails]
    metadata: NotRequired[dict[str, str]]
    paymentSettings: SubscriptionPaymentSettings
    createdTimestamp: int


class Subscriptions(TypedDict):
    items: List[Subscription]
    paginationToken: str
