from typing_extensions import List, TypedDict


class Webhook(TypedDict):
    id: str
    active: bool
    eventTypes: List[str]
    createdTimestamp: int


class Webhooks(TypedDict):
    items: List[Webhook]


class CreatedWebhook(TypedDict):
    secret: str
    id: str
    active: bool
    eventTypes: List[str]
    createdTimestamp: int
