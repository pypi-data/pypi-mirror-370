from typing_extensions import List, NotRequired, TypedDict


class File(TypedDict):
    id: str
    name: str
    type: str
    category: str
    metadata: NotRequired[dict[str, str]]
    createdTimestamp: int
    lastUpdatedTimestamp: int
    sizeInBytes: NotRequired[int]


class Files(TypedDict):
    items: List[File]
    paginationToken: NotRequired[str]
