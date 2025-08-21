from typing_extensions import Any, List, NotRequired, TypedDict


class EventCustomer(TypedDict):
    id: NotRequired[str]


class PaymentMethodTokenizedDetails(TypedDict):
    id: str
    stored: bool


class PaymentMethod(TypedDict):
    tokenizedDetails: PaymentMethodTokenizedDetails


class EventEndpoint(TypedDict):
    webhookId: str
    acknowledged: bool
    attempts: int


class Event(TypedDict):
    id: str
    eventType: str
    data: dict[str, Any]
    endpoints: List[EventEndpoint]
    accountId: NotRequired[str]
    createdTimestamp: int


class Events(TypedDict):
    items: List[Event]


class PausePaymentDetail(TypedDict):
    reason: NotRequired[str]
    resumeAtTimestamp: NotRequired[int]
    pausedAtTimestamp: int
