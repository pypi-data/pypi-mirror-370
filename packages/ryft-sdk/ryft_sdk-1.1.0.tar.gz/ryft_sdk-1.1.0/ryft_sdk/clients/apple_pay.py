from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.apple_pay.dto.apple_pay import (
    ApplePayWebDomain,
    ApplePayWebDomains,
    ApplePayWebSession,
)
from ryft_sdk.models.apple_pay.req.apple_pay_req import CreateApplePayWebSessionReq


class ApplePayClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.domains_path = "apple-pay/web-domains"
        self.sessions_path = "apple-pay/sessions"

    async def register_domain(
        self, domain: str, account_id: Optional[str] = None
    ) -> ApplePayWebDomain:
        return cast(
            ApplePayWebDomain,
            self.client.post(
                self.domains_path,
                {
                    "domainName": domain,
                },
                account_id,
            ),
        )

    async def list_domains(
        self,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[int] = None,
        account_id: Optional[str] = None,
    ) -> ApplePayWebDomains:
        return cast(
            ApplePayWebDomains,
            self.client.get(
                self.domains_path,
                {
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
                account_id,
            ),
        )

    async def get_domain(
        self, id: str, account_id: Optional[str] = None
    ) -> ApplePayWebDomain:
        return cast(
            ApplePayWebDomain,
            self.client.get(f"{self.domains_path}/{id}", {}, account_id),
        )

    async def delete_domain(
        self, id: str, account_id: Optional[str] = None
    ) -> ApplePayWebDomain:
        return cast(
            ApplePayWebDomain,
            self.client.delete(f"{self.domains_path}/{id}", account=account_id),
        )

    async def create_session(
        self, req: CreateApplePayWebSessionReq
    ) -> ApplePayWebSession:
        return cast(
            ApplePayWebSession, self.client.post(self.sessions_path, cast(dict, req))
        )
