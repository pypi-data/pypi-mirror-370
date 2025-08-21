from typing_extensions import List, NotRequired, TypedDict
from ryft_sdk.models.address import AccountAddress
from ryft_sdk.models.persons.dto.persons_verification import PersonVerification


class Document(TypedDict):
    type: str
    front: str
    back: NotRequired[str]
    country: NotRequired[str]


class Person(TypedDict):
    id: str
    firstName: str
    lastName: str
    email: NotRequired[str]
    dateOfBirth: NotRequired[str]
    countryOfBirth: NotRequired[str]
    gender: str
    nationalities: List[str]
    address: AccountAddress
    phoneNumber: str
    businessRoles: List[str]
    verification: PersonVerification
    documents: List[Document]
    metadata: NotRequired[dict[str, str]]
    createdTimestamp: int
    lastUpdatedTimestamp: int


class Persons(TypedDict):
    items: List[Person]
    paginationToken: NotRequired[str]
