from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.platform_fees.dto.platform_fees import (
    PlatformFee,
    PlatformFeeRefunds,
    PlatformFees,
)


class PlatformFeesClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "platform-fees"

    async def list(
        self, ascending: Optional[bool] = None, limit: Optional[int] = None
    ) -> PlatformFees:
        return cast(
            PlatformFees,
            self.client.get(
                self.path,
                {
                    "ascending": ascending,
                    "limit": limit,
                },
            ),
        )

    async def get(self, id: str) -> PlatformFee:
        return cast(PlatformFee, self.client.get(f"{self.path}/{id}"))

    async def get_refunds(self, id: str) -> PlatformFeeRefunds:
        return cast(PlatformFeeRefunds, self.client.get(f"{self.path}/{id}/refunds"))
