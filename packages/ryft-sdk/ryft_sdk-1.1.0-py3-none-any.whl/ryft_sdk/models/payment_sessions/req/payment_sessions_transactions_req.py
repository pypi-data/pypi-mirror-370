from typing_extensions import NotRequired, TypedDict

from ryft_sdk.models.payment_sessions.req.payment_sessions_req import (
    SplitPaymentsRequest,
)


class CapturePaymentSessionRequest(TypedDict):
    amount: NotRequired[int]
    captureType: NotRequired[str]
    platformFee: NotRequired[int]
    splits: NotRequired[SplitPaymentsRequest]


class CaptureTransactionRequest(TypedDict):
    id: str


class RefundPaymentSessionRequest(TypedDict):
    amount: NotRequired[int]
    reason: NotRequired[str]
    refundPlatformFee: NotRequired[bool]
    splits: NotRequired[SplitPaymentsRequest]
    captureTransaction: NotRequired[CaptureTransactionRequest]
