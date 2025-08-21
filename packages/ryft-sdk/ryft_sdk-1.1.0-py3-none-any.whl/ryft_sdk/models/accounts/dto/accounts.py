from typing_extensions import List, Literal, NotRequired, TypedDict, Union
from ryft_sdk.models.address import AccountAddress


class AccountAuthorization(TypedDict):
    createdTimestamp: int
    expiresTimestamp: int
    url: str


class AccountDocument(TypedDict):
    type: str
    front: str
    back: NotRequired[str]
    status: str
    invalidReason: NotRequired[str]
    country: NotRequired[str]
    assignedTimestamp: int
    lastUpdatedTimestamp: int


class AccountBusiness(TypedDict):
    name: str
    type: str
    registrationNumber: str
    registrationDate: NotRequired[str]
    registeredAddress: AccountAddress
    contactEmail: str
    phoneNumber: NotRequired[str]
    tradingName: NotRequired[str]
    tradingAddress: NotRequired[AccountAddress]
    tradingCountries: NotRequired[List[str]]
    websiteUrl: NotRequired[str]
    documents: List[AccountDocument]


class AccountIndividual(TypedDict):
    firstName: str
    middleNames: NotRequired[str]
    lastName: str
    email: str
    dateOfBirth: str
    countryOfBirth: NotRequired[str]
    gender: Union[Literal["Male"], Literal["Female"]]
    nationalities: List[str]
    address: AccountAddress
    phoneNumber: NotRequired[str]
    documents: List[AccountDocument]


class AccountRequiredField(TypedDict):
    name: str


class AccountRequiredDocument(TypedDict):
    category: str
    types: List[str]
    quantity: int


class AccountError(TypedDict):
    id: str
    code: str
    description: str


class AccountRequiredPerson(TypedDict):
    role: str
    quantity: int


class AccountPerson(TypedDict):
    status: str
    required: List[AccountRequiredPerson]


class AccountVerification(TypedDict):
    status: str
    requiredFields: List[AccountRequiredField]
    requiredDocuments: List[AccountRequiredDocument]
    errors: List[AccountError]
    persons: List[AccountPerson]


class AccountSchedule(TypedDict):
    type: str


class AccountPayout(TypedDict):
    schedule: AccountSchedule


class AccountSettings(TypedDict):
    payouts: AccountPayout


class AccountCapability(TypedDict):
    status: str
    requested: bool
    requiredFields: List[AccountRequiredField]
    disabledReason: NotRequired[str]
    requestedTimestamp: int
    lastUpdatedTimestamp: int


class AccountCapabilities(TypedDict):
    visaPayments: AccountCapability
    mastercardPayments: AccountCapability
    amexPayments: AccountCapability


class AccountTermsOfServiceAcceptance(TypedDict):
    ipAddress: str
    userAgent: NotRequired[str]
    when: int


class AccountTermsOfService(TypedDict):
    acceptance: AccountTermsOfServiceAcceptance


class SubAccount(TypedDict):
    id: str
    type: str
    frozen: bool
    email: NotRequired[str]
    onboardingFlow: str
    entityType: str
    business: NotRequired[AccountBusiness]
    individual: NotRequired[AccountIndividual]
    verification: AccountVerification
    metadata: NotRequired[dict[str, str]]
    settings: AccountSettings
    capabilities: AccountCapabilities
    termsOfService: NotRequired[AccountTermsOfService]
    createdTimestamp: int
