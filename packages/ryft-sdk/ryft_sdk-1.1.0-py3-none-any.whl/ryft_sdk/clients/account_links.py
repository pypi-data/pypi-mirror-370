from typing import cast
from ryft_sdk.client import RyftClient
from ryft_sdk.models.account_links.dto.account_links import TemporaryAccountLink
from ryft_sdk.models.account_links.req.account_links_req import CreateTmpLinkReq


class AccountLinksClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "account-links"

    async def create_tmp_link(self, req: CreateTmpLinkReq) -> TemporaryAccountLink:
        return cast(TemporaryAccountLink, self.client.post(self.path, cast(dict, req)))
