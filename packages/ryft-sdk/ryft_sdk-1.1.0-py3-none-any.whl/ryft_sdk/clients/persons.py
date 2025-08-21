from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.deleted_resource_resp import DeletedResourceResp
from ryft_sdk.models.persons.dto.persons import Person, Persons
from ryft_sdk.models.persons.req.persons_req import (
    CreatePersonRequest,
    UpdatePersonRequest,
)


class PersonsClient:
    def __init__(self, client: RyftClient):
        self.client = client

    async def create(self, id: str, req: CreatePersonRequest) -> Person:
        return cast(Person, self.client.post(f"accounts/{id}/persons", cast(dict, req)))

    async def list(
        self,
        id: str,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
    ) -> Persons:
        return cast(
            Persons,
            self.client.get(
                f"accounts/{id}/persons",
                {
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )

    async def get(self, id: str, person_id: str) -> Person:
        return cast(Person, self.client.get(f"accounts/{id}/persons/{person_id}"))

    async def update(self, id: str, person_id: str, req: UpdatePersonRequest) -> Person:
        return cast(
            Person,
            self.client.patch(f"accounts/{id}/persons/{person_id}", cast(dict, req)),
        )

    async def delete(self, id: str, person_id: str) -> DeletedResourceResp:
        return cast(
            DeletedResourceResp,
            self.client.delete(f"accounts/{id}/persons/{person_id}", {}),
        )
