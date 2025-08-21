from typing_extensions import NotRequired, TypedDict
from ryft_sdk.models.shipping_details import ShippingDetails


class SubscriptionCustomerRequest(TypedDict):
    id: str


class SubscriptionIntervalRequest(TypedDict):
    unit: str
    count: int
    times: NotRequired[int]


class SubscriptionPriceRequest(TypedDict):
    amount: int
    currency: str
    interval: SubscriptionIntervalRequest


class StatementDescriptorRequest(TypedDict):
    descriptor: str
    city: str


class PaymentSettingsRequest(TypedDict):
    statementDescriptor: StatementDescriptorRequest


class CreateSubscriptionRequest(TypedDict):
    customer: SubscriptionCustomerRequest
    price: SubscriptionPriceRequest
    paymentMethod: SubscriptionCustomerRequest
    description: NotRequired[str]
    billingCycleTimestamp: NotRequired[int]
    metadata: NotRequired[dict[str, str]]
    shippingDetails: NotRequired[ShippingDetails]
    paymentSettings: NotRequired[PaymentSettingsRequest]


class SubscriptionUpdatePriceRequest(TypedDict):
    amount: int
    interval: NotRequired[SubscriptionIntervalRequest]


class UpdateSubscriptionRequest(TypedDict):
    price: NotRequired[SubscriptionUpdatePriceRequest]
    paymentMethod: NotRequired[SubscriptionCustomerRequest]
    description: NotRequired[str]
    billingCycleTimestamp: NotRequired[int]
    metadata: NotRequired[dict[str, str]]
    shippingDetails: NotRequired[ShippingDetails]
    paymentSettings: NotRequired[PaymentSettingsRequest]


class PauseSubscriptionRequest(TypedDict):
    reason: NotRequired[str]
    resumeTimestamp: NotRequired[int]
    unschedule: NotRequired[bool]
