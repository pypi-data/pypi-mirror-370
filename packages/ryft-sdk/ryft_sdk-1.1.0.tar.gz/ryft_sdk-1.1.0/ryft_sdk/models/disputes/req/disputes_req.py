from typing_extensions import List, NotRequired, TypedDict
from ryft_sdk.models.disputes.dto.disputes import (
    DisputeEvidenceFile,
    DisputeEvidenceTextEntries,
)


class AddDisputeEvidenceRequest(TypedDict):
    text: NotRequired[DisputeEvidenceTextEntries]
    files: NotRequired[DisputeEvidenceFile]


class DeleteDisputeEvidenceRequest(TypedDict):
    text: List[str]
    files: List[str]
