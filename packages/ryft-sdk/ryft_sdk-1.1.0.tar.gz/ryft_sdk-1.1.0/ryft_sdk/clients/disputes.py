from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.disputes.dto.disputes import Dispute, Disputes
from ryft_sdk.models.disputes.req.disputes_req import (
    AddDisputeEvidenceRequest,
    DeleteDisputeEvidenceRequest,
)


class DisputesClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "disputes"

    async def list(
        self,
        startTimestamp: Optional[int] = None,
        endTimestamp: Optional[int] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
    ) -> Disputes:
        return cast(
            Disputes,
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

    async def get(self, id: str) -> Dispute:
        return cast(Dispute, self.client.get(f"{self.path}/{id}"))

    async def accept(self, id: str) -> Dispute:
        return cast(Dispute, self.client.post(f"{self.path}/{id}/accept", {}))

    async def challenge(self, id: str) -> Dispute:
        return cast(Dispute, self.client.post(f"{self.path}/{id}/challenge", {}))

    async def add_evidence(self, id: str, req: AddDisputeEvidenceRequest) -> Dispute:
        return cast(
            Dispute, self.client.patch(f"{self.path}/{id}/evidence", cast(dict, req))
        )

    async def delete_evidence(
        self, id: str, req: DeleteDisputeEvidenceRequest
    ) -> Dispute:
        return cast(
            Dispute, self.client.delete(f"{self.path}/{id}/evidence", cast(dict, req))
        )
