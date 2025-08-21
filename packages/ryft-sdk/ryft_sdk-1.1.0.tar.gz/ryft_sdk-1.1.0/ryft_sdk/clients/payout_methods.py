from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.deleted_resource_resp import DeletedResourceResp
from ryft_sdk.models.payout_methods.dto.payout_methods import (
    PayoutMethod,
    PayoutMethods,
)
from ryft_sdk.models.payout_methods.req.payout_methods import (
    CreatePayoutMethodRequest,
    UpdatePayoutMethodRequest,
)


class PayoutMethodsClient:
    def __init__(self, client: RyftClient):
        self.client = client

    async def create(self, id: str, req: CreatePayoutMethodRequest) -> PayoutMethod:
        return cast(
            PayoutMethod,
            self.client.post(f"accounts/{id}/payout-methods", cast(dict, req)),
        )

    async def list(
        self,
        id: str,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
    ) -> PayoutMethods:
        return cast(
            PayoutMethods,
            self.client.get(
                f"accounts/{id}/payout-methods",
                {
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )

    async def get(self, id: str, payout_method_id) -> PayoutMethod:
        return cast(
            PayoutMethod,
            self.client.get(f"accounts/{id}/payout-methods/{payout_method_id}"),
        )

    async def update(
        self, id: str, payout_method_id: str, req: UpdatePayoutMethodRequest
    ) -> PayoutMethod:
        return cast(
            PayoutMethod,
            self.client.patch(
                f"accounts/{id}/payout-methods/{payout_method_id}", cast(dict, req)
            ),
        )

    async def delete(self, id: str, payout_method_id: str) -> DeletedResourceResp:
        return cast(
            DeletedResourceResp,
            self.client.delete(f"accounts/{id}/payout-methods/{payout_method_id}", {}),
        )
