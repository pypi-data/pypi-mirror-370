from typing_extensions import List, NotRequired, TypedDict
from ryft_sdk.models.payment_sessions.dto.payment_sessions import (
    PaymentSessionPaymentMethod,
    SplitPaymentDetail,
)


class PaymentTransaction(TypedDict):
    id: str
    paymentSessionId: str
    amount: int
    currency: str
    type: str
    status: str
    refundedAmount: NotRequired[int]
    platformFee: NotRequired[int]
    platformFeeRefundedAmount: NotRequired[int]
    processingFee: NotRequired[int]
    reason: NotRequired[str]
    captureType: NotRequired[str]
    paymentMethod: NotRequired[PaymentSessionPaymentMethod]
    splitPaymentDetail: NotRequired[SplitPaymentDetail]
    createdTimestamp: int
    lastUpdatedTimestamp: int


class PaymentTransactions(TypedDict):
    items: List[PaymentTransaction]
    paginationToken: NotRequired[str]
