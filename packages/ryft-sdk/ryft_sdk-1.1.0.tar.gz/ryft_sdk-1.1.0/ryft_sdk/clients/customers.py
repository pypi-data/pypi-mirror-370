from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.customers.dto.customers import Customer, Customers
from ryft_sdk.models.customers.req.customers_req import (
    CreateCustomerRequest,
    UpdateCustomerRequest,
)
from ryft_sdk.models.deleted_resource_resp import DeletedResourceResp
from ryft_sdk.models.payment_methods.dto.payment_methods_req import PaymentMethods


class CustomersClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "customers"

    async def create(self, req: CreateCustomerRequest) -> Customer:
        return cast(Customer, self.client.post(self.path, cast(dict, req)))

    async def list(
        self,
        email: Optional[str] = None,
        startTimestamp: Optional[int] = None,
        endTimestamp: Optional[int] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
    ) -> Customers:
        return cast(
            Customers,
            self.client.get(
                self.path,
                {
                    "email": email,
                    "startTimestamp": startTimestamp,
                    "endTimestamp": endTimestamp,
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )

    async def get(self, id: str) -> Customer:
        return cast(Customer, self.client.get(f"{self.path}/{id}"))

    async def update(self, id: str, req: UpdateCustomerRequest) -> Customer:
        return cast(Customer, self.client.patch(f"{self.path}/{id}", cast(dict, req)))

    async def delete(self, id: str) -> DeletedResourceResp:
        return cast(DeletedResourceResp, self.client.delete(f"{self.path}/{id}", {}))

    async def get_payment_methods(self, id: str) -> PaymentMethods:
        return cast(
            PaymentMethods, self.client.get(f"{self.path}/{id}/payment-methods", {})
        )
