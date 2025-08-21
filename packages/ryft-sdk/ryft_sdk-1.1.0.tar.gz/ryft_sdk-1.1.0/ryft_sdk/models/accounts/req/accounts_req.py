from typing_extensions import List, Literal, NotRequired, TypedDict, Union
from ryft_sdk.models.address import AccountAddress


class AccountDocumentReq(TypedDict):
    type: str
    front: str
    back: NotRequired[str]
    country: NotRequired[str]


class AccountBusinessReq(TypedDict):
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
    documents: NotRequired[List[AccountDocumentReq]]


class AccountIndividualReq(TypedDict):
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
    documents: NotRequired[List[AccountDocumentReq]]


class AccountPayoutScheduleReq(TypedDict):
    type: str


class AccountPayoutReq(TypedDict):
    schedule: AccountPayoutScheduleReq


class AccountSettingsReq(TypedDict):
    payouts: AccountPayoutReq


class AccountAcceptanceDetailsReq(TypedDict):
    ipAddress: str
    userAgent: NotRequired[str]
    when: NotRequired[int]


class AccountTermsOfServiceReq(TypedDict):
    acceptance: AccountAcceptanceDetailsReq


class CreateSubAccountRequest(TypedDict):
    onboardingFlow: NotRequired[str]
    email: NotRequired[str]
    entityType: NotRequired[str]
    business: NotRequired[AccountBusinessReq]
    individual: NotRequired[AccountIndividualReq]
    metadata: NotRequired[dict[str, str]]
    settings: NotRequired[AccountSettingsReq]
    termsOfService: NotRequired[AccountTermsOfServiceReq]


class UpdateBusinessReq(TypedDict):
    name: NotRequired[str]
    type: str
    registrationNumber: NotRequired[str]
    registrationDate: NotRequired[str]
    registeredAddress: NotRequired[AccountAddress]
    contactEmail: NotRequired[str]
    phoneNumber: NotRequired[str]
    tradingName: NotRequired[str]
    tradingAddress: NotRequired[AccountAddress]
    tradingCountries: NotRequired[List[str]]
    websiteUrl: NotRequired[str]
    documents: NotRequired[List[AccountDocumentReq]]


class UpdateSubAccountRequest(TypedDict):
    entityType: NotRequired[str]
    business: NotRequired[UpdateBusinessReq]
    individual: NotRequired[AccountIndividualReq]
    metadata: NotRequired[dict[str, str]]
    settings: NotRequired[AccountSettingsReq]
    termsOfService: NotRequired[AccountTermsOfServiceReq]
