from typing_extensions import List, NotRequired, TypedDict


class DisputeReason(TypedDict):
    code: str
    description: str


class DisputeCard(TypedDict):
    scheme: str
    last4: str


class DisputePaymentMethod(TypedDict):
    card: DisputeCard


class DisputePaymentSession(TypedDict):
    id: str
    paymentType: str
    paymentMethod: DisputePaymentMethod


class DisputeEvidenceTextEntries(TypedDict):
    billingAddress: str
    shippingAddress: str
    duplicateTransaction: str
    uncategorised: str


class DisputeFile(TypedDict):
    id: str


class DisputeEvidenceFile(TypedDict):
    proofOfDelivery: NotRequired[DisputeFile]
    customerSignature: NotRequired[DisputeFile]
    receipt: NotRequired[DisputeFile]
    shippingConfirmation: NotRequired[DisputeFile]
    customerCommunication: NotRequired[DisputeFile]
    refundPolicy: NotRequired[DisputeFile]
    recurringPaymentAgreement: NotRequired[DisputeFile]
    uncategorised: NotRequired[DisputeFile]


class DisputeEvidence(TypedDict):
    text: NotRequired[DisputeEvidenceTextEntries]
    files: NotRequired[DisputeEvidenceFile]


class DisputeCustomer(TypedDict):
    email: NotRequired[str]
    id: NotRequired[str]
    createdTimestamp: NotRequired[int]


class Dispute(TypedDict):
    id: str
    amount: int
    currency: str
    status: str
    category: str
    reason: DisputeReason
    respondBy: int
    recommendedEvidence: List[str]
    paymentSession: DisputePaymentSession
    evidence: NotRequired[DisputeEvidence]
    customer: NotRequired[DisputeCustomer]
    subAccount: NotRequired[DisputeFile]
    createdTimestamp: int
    lastUpdatedTimestamp: int


class Disputes(TypedDict):
    items: List[Dispute]
    paginationToken: NotRequired[str]
