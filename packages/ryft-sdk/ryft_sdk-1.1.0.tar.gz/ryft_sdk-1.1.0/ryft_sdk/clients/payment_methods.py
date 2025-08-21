from typing import cast
from ryft_sdk.client import RyftClient
from ryft_sdk.models.deleted_resource_resp import DeletedResourceResp
from ryft_sdk.models.payment_methods.dto.payment_methods import PaymentMethod
from ryft_sdk.models.payment_methods.req.payment_methods_req import (
    UpdatePaymentMethodRequest,
)


class PaymentMethodsClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "payment-methods"

    async def get(self, id: str) -> PaymentMethod:
        return cast(PaymentMethod, self.client.get(f"{self.path}/{id}"))

    async def update(self, id: str, req: UpdatePaymentMethodRequest) -> PaymentMethod:
        return cast(
            PaymentMethod, self.client.patch(f"{self.path}/{id}", cast(dict, req))
        )

    async def delete(self, id: str) -> DeletedResourceResp:
        return cast(DeletedResourceResp, self.client.delete(f"{self.path}/{id}"))
