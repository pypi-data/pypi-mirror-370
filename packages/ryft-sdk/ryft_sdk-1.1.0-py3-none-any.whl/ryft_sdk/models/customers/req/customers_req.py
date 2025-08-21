from typing_extensions import NotRequired, TypedDict


class CreateCustomerRequest(TypedDict):
    email: str
    firstName: NotRequired[str]
    lastName: NotRequired[str]
    homePhoneNumber: NotRequired[str]
    mobilePhoneNumber: NotRequired[str]
    metadata: NotRequired[dict[str, str]]


class UpdateCustomerRequest(TypedDict):
    firstName: NotRequired[str]
    lastName: NotRequired[str]
    homePhoneNumber: NotRequired[str]
    mobilePhoneNumber: NotRequired[str]
    metadata: NotRequired[dict[str, str]]
    defaultPaymentMethod: NotRequired[str]
