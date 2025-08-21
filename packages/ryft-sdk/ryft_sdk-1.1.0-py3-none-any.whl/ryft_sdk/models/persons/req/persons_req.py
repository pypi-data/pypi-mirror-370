from typing_extensions import List, NotRequired, TypedDict
from ryft_sdk.models.address import AccountAddress


class DocumentRequest(TypedDict):
    type: str
    front: str
    back: NotRequired[str]
    country: NotRequired[str]


class CreatePersonRequest(TypedDict):
    firstName: str
    middleNames: NotRequired[str]
    lastName: str
    email: str
    dateOfBirth: str
    countryOfBirth: NotRequired[str]
    gender: str
    nationalities: List[str]
    address: AccountAddress
    phoneNumber: str
    businessRoles: List[str]
    documents: List[DocumentRequest]
    metadata: NotRequired[dict[str, str]]


class UpdatePersonRequest(TypedDict):
    firstName: NotRequired[str]
    middleNames: NotRequired[str]
    lastName: NotRequired[str]
    email: NotRequired[str]
    dateOfBirth: NotRequired[str]
    countryOfBirth: NotRequired[str]
    gender: NotRequired[str]
    nationalities: NotRequired[List[str]]
    address: NotRequired[AccountAddress]
    phoneNumber: NotRequired[str]
    businessRoles: NotRequired[List[str]]
    documents: NotRequired[List[DocumentRequest]]
    metadata: NotRequired[dict[str, str]]
