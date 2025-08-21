from typing_extensions import TypedDict


class VerificationError(TypedDict):
    code: str
    id: str
    description: str
