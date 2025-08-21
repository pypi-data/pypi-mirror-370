from typing_extensions import List, NotRequired, TypedDict


class ApplePayWebDomain(TypedDict):
    id: str
    domainName: str
    createdTimestamp: int


class ApplePayWebDomains(TypedDict):
    items: List[ApplePayWebDomain]
    paginationToken: NotRequired[str]


class ApplePayWebSession(TypedDict):
    sessionObject: str
