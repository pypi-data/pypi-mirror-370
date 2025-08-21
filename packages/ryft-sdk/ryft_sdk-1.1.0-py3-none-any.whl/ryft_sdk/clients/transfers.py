from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.transfers.dto.transfers import Transfer, Transfers
from ryft_sdk.models.transfers.req.transfers_req import CreateTransferRequest


class TransfersClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "transfers"

    async def create(self, req: CreateTransferRequest) -> Transfer:
        return cast(Transfer, self.client.post(self.path, cast(dict, req)))

    async def list(
        self,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[int] = None,
    ) -> Transfers:
        return cast(
            Transfers,
            self.client.get(
                self.path,
                {
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )

    async def get(self, id: str) -> Transfer:
        return cast(Transfer, self.client.get(f"{self.path}/{id}"))
