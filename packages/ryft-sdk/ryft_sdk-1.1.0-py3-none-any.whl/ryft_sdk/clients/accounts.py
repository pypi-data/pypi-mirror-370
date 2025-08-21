from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.accounts.dto.accounts import AccountAuthorization, SubAccount
from ryft_sdk.models.accounts.dto.payouts import Payout, Payouts
from ryft_sdk.models.accounts.req.accounts_req import (
    CreateSubAccountRequest,
    UpdateSubAccountRequest,
)
from ryft_sdk.models.accounts.req.authlink_req import CreateAuthLinkReq
from ryft_sdk.models.accounts.req.payouts_req import CreatePayoutRequest


class AccountsClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "accounts"

    async def create(self, req: CreateSubAccountRequest) -> SubAccount:
        return cast(SubAccount, self.client.post(self.path, cast(dict, req)))

    async def get(self, id: str) -> SubAccount:
        return cast(SubAccount, self.client.get(f"{self.path}/{id}"))

    async def update(self, id: str, req: UpdateSubAccountRequest) -> SubAccount:
        return cast(SubAccount, self.client.patch(f"{self.path}/{id}", cast(dict, req)))

    async def verify(self, id: str) -> SubAccount:
        return cast(SubAccount, self.client.post(f"{self.path}/{id}/verify", {}))

    async def create_payout(self, id: str, req: CreatePayoutRequest) -> Payout:
        return cast(
            Payout, self.client.post(f"{self.path}/{id}/payouts", cast(dict, req))
        )

    async def list_payouts(
        self,
        id: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[int] = None,
    ) -> Payouts:
        return cast(
            Payouts,
            self.client.get(
                f"{self.path}/{id}/payouts",
                {
                    "start": start,
                    "end": end,
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )

    async def get_payout(self, id: str, payoutId: str) -> Payout:
        return cast(Payout, self.client.get(f"{self.path}/{id}/payouts/{payoutId}"))

    async def create_auth_link(self, req: CreateAuthLinkReq) -> AccountAuthorization:
        return cast(
            AccountAuthorization,
            self.client.post(f"{self.path}/authorize", cast(dict, req)),
        )
