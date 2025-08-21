from typing import cast
from ryft_sdk.client import RyftClient
from ryft_sdk.models.deleted_resource_resp import DeletedResourceResp
from ryft_sdk.models.webhooks.dto.webhooks import CreatedWebhook, Webhook, Webhooks
from ryft_sdk.models.webhooks.req.webhooks_req import (
    CreateWebhookRequest,
    UpdateWebhookRequest,
)


class WebhooksClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "webhooks"

    async def create(self, req: CreateWebhookRequest) -> CreatedWebhook:
        return cast(CreatedWebhook, self.client.post(self.path, cast(dict, req)))

    async def list(self) -> Webhooks:
        return cast(Webhooks, self.client.get(self.path))

    async def get(self, id: str) -> Webhook:
        return cast(Webhook, self.client.get(f"{self.path}/{id}"))

    async def update(self, id: str, req: UpdateWebhookRequest) -> Webhook:
        return cast(Webhook, self.client.patch(f"{self.path}/{id}", cast(dict, req)))

    async def delete(self, id: str) -> DeletedResourceResp:
        return cast(DeletedResourceResp, self.client.delete(f"{self.path}/{id}", {}))
