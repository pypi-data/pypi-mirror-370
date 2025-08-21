from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.events.dto.events import Event, Events


class EventsClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "events"

    async def get(self, id: str, account: Optional[str] = None) -> Event:
        return cast(Event, self.client.get(f"{self.path}/{id}", account=account))

    async def list(
        self,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        account: Optional[str] = None,
        startsAfter: Optional[str] = None,
    ) -> Events:
        return cast(
            Events,
            self.client.get(
                f"{self.path}",
                {
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
                account=account,
            ),
        )
