from typing_extensions import List, NotRequired, TypedDict

from ryft_sdk.models.persons.dto.verification_error import VerificationError


class VerificationRequiredField(TypedDict):
    name: str


class VerificationRequiredDocuments(TypedDict):
    category: str
    types: List[str]
    quantity: int


class PersonVerification(TypedDict):
    status: str
    requiredFields: List[VerificationRequiredField]
    requiredDocuments: VerificationRequiredDocuments
    errors: NotRequired[List[VerificationError]]
