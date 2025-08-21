from typing_extensions import NotRequired, TypedDict


class Address(TypedDict):
    firstName: NotRequired[str]
    lastName: NotRequired[str]
    lineOne: NotRequired[str]
    lineTwo: NotRequired[str]
    city: NotRequired[str]
    country: str
    postalCode: str
    region: NotRequired[str]


class AccountAddress(TypedDict):
    lineOne: str
    lineTwo: NotRequired[str]
    city: NotRequired[str]
    country: str
    postalCode: str
    region: NotRequired[str]
