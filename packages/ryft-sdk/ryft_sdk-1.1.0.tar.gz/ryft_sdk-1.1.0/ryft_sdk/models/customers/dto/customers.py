from typing_extensions import List, NotRequired, TypedDict


class Customer(TypedDict):
    id: str
    email: str
    firstName: NotRequired[str]
    lastName: NotRequired[str]
    homePhoneNumber: NotRequired[str]
    mobilePhoneNumber: NotRequired[str]
    defaultPaymentMethod: NotRequired[str]
    metadata: NotRequired[dict[str, str]]
    createdTimestamp: int


class Customers(TypedDict):
    items: List[Customer]
    paginationToken: NotRequired[str]
