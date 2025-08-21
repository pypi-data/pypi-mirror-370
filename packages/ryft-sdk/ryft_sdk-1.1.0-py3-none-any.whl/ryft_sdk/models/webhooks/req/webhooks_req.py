from typing_extensions import List, TypedDict


class CreateWebhookRequest(TypedDict):
    url: str
    active: bool
    eventTypes: List[str]


class UpdateWebhookRequest(TypedDict):
    url: str
    active: bool
    eventTypes: List[str]
