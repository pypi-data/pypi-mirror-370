from typing import Optional, cast
from ryft_sdk.client import RyftClient
from ryft_sdk.models.payment_sessions.dto.payment_sessions import (
    PaymentSession,
    PaymentSessions,
)
from ryft_sdk.models.payment_sessions.dto.payment_transactions import (
    PaymentTransaction,
    PaymentTransactions,
)
from ryft_sdk.models.payment_sessions.req.payment_sessions_req import (
    AttemptPaymentSessionRequest,
    ContinuePaymentSessionRequest,
    CreatePaymentSessionRequest,
    UpdatePaymentSessionRequest,
)
from ryft_sdk.models.payment_sessions.req.payment_sessions_transactions_req import (
    CapturePaymentSessionRequest,
    RefundPaymentSessionRequest,
)


class PaymentSessionsClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "payment-sessions"

    async def create(
        self, req: CreatePaymentSessionRequest, account: Optional[str] = None
    ) -> PaymentSession:
        return cast(
            PaymentSession,
            self.client.post(self.path, cast(dict, req), account=account),
        )

    async def list(
        self,
        startTimestamp: Optional[int] = None,
        endTimestamp: Optional[int] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
        account: Optional[str] = None,
    ) -> PaymentSessions:
        return cast(
            PaymentSessions,
            self.client.get(
                self.path,
                {
                    "startTimestamp": startTimestamp,
                    "endTimestamp": endTimestamp,
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
                account=account,
            ),
        )

    async def get(self, id: str, account: Optional[str] = None) -> PaymentSession:
        return cast(
            PaymentSession, self.client.get(f"{self.path}/{id}", account=account)
        )

    async def update(
        self, id: str, req: UpdatePaymentSessionRequest, account: Optional[str] = None
    ) -> PaymentSession:
        return cast(
            PaymentSession,
            self.client.patch(f"{self.path}/{id}", cast(dict, req), account=account),
        )

    async def attempt_payment(
        self, req: AttemptPaymentSessionRequest, account: Optional[str] = None
    ) -> PaymentSession:
        return cast(
            PaymentSession,
            self.client.post(
                f"{self.path}/attempt-payment", cast(dict, req), account=account
            ),
        )

    async def continue_payment(
        self, req: ContinuePaymentSessionRequest, account: Optional[str] = None
    ) -> PaymentSession:
        return cast(
            PaymentSession,
            self.client.post(
                f"{self.path}/continue-payment", cast(dict, req), account=account
            ),
        )

    async def list_transactions(
        self,
        id: str,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
        account: Optional[str] = None,
    ) -> PaymentTransactions:
        return cast(
            PaymentTransactions,
            self.client.get(
                f"{self.path}/{id}/transactions",
                {"ascending": ascending, "limit": limit, "startsAfter": startsAfter},
                account=account,
            ),
        )

    async def get_transaction(
        self, id: str, transaction_id: str, account: Optional[str] = None
    ) -> PaymentTransaction:
        return cast(
            PaymentTransaction,
            self.client.get(
                f"{self.path}/{id}/transactions/{transaction_id}", account=account
            ),
        )

    async def capture(
        self, id: str, req: CapturePaymentSessionRequest, account: Optional[str] = None
    ) -> PaymentTransaction:
        return cast(
            PaymentTransaction,
            self.client.post(
                f"{self.path}/{id}/captures", cast(dict, req), account=account
            ),
        )

    async def void(self, id: str, account: Optional[str] = None) -> PaymentTransaction:
        return cast(
            PaymentTransaction,
            self.client.post(f"{self.path}/{id}/voids", {}, account=account),
        )

    async def refund(
        self, id: str, req: RefundPaymentSessionRequest, account: Optional[str] = None
    ) -> PaymentTransaction:
        return cast(
            PaymentTransaction,
            self.client.post(
                f"{self.path}/{id}/refunds", cast(dict, req), account=account
            ),
        )
