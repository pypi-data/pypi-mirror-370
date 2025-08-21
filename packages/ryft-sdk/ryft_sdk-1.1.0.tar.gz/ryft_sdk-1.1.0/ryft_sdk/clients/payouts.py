from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.accounts.req.payouts_req import CreatePayoutRequest
from ryft_sdk.models.payouts.dto.payouts import Payout, Payouts


class PayoutsClient:
    def __init__(self, client: RyftClient):
        self.client = client

    async def create(self, id: str, req: CreatePayoutRequest) -> Payout:
        return cast(Payout, self.client.post(f"accounts/{id}/payouts", cast(dict, req)))

    async def get(self, id: str, payout_id: str) -> Payout:
        return cast(Payout, self.client.get(f"accounts/{id}/payouts/{payout_id}"))

    async def list(
        self,
        id: str,
        startTimestamp: Optional[int] = None,
        endTimestamp: Optional[int] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[int] = None,
    ) -> Payouts:
        return cast(
            Payouts,
            self.client.get(
                f"accounts/{id}/payouts",
                {
                    "startTimestamp": startTimestamp,
                    "endTimestamp": endTimestamp,
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )
