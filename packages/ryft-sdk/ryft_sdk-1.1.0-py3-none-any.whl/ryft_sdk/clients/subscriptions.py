from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.deleted_resource_resp import DeletedResourceResp
from ryft_sdk.models.subscriptions.dto.payment_session import PaymentSessions
from ryft_sdk.models.subscriptions.dto.subscriptions import Subscription
from ryft_sdk.models.subscriptions.req.subscriptions_req import (
    CreateSubscriptionRequest,
)
from ryft_sdk.models.subscriptions.req.subscriptions_req import (
    PauseSubscriptionRequest,
    UpdateSubscriptionRequest,
)


class SubscriptionsClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "subscriptions"

    async def create(self, req: CreateSubscriptionRequest) -> Subscription:
        return cast(Subscription, self.client.post(self.path, cast(dict, req)))

    async def list(
        self,
        startTimestamp: Optional[int] = None,
        endTimestamp: Optional[int] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
    ) -> Subscription:
        return cast(
            Subscription,
            self.client.get(
                self.path,
                {
                    "startTimestamp": startTimestamp,
                    "endTimestamp": endTimestamp,
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )

    async def get(self, id: str) -> Subscription:
        return cast(Subscription, self.client.get(f"{self.path}/{id}"))

    async def update(self, id: str, req: UpdateSubscriptionRequest) -> Subscription:
        return cast(
            Subscription, self.client.patch(f"{self.path}/{id}", cast(dict, req))
        )

    async def pause(
        self, id: str, req: Optional[PauseSubscriptionRequest] = None
    ) -> Subscription:
        return cast(
            Subscription, self.client.patch(f"{self.path}/{id}/pause", cast(dict, req))
        )

    async def resume(self, id: str) -> Subscription:
        return cast(Subscription, self.client.patch(f"{self.path}/{id}/resume", {}))

    async def delete(self, id: str) -> DeletedResourceResp:
        return cast(DeletedResourceResp, self.client.delete(f"{self.path}/{id}", {}))

    async def get_payment_sessions(
        self,
        id: str,
        startTimestamp: Optional[int] = None,
        endTimestamp: Optional[int] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
    ) -> PaymentSessions:
        return cast(
            PaymentSessions,
            self.client.get(
                f"{self.path}/{id}/payment-sessions",
                {
                    "startTimestamp": startTimestamp,
                    "endTimestamp": endTimestamp,
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )
