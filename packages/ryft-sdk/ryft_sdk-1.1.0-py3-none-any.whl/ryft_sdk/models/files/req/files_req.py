from typing_extensions import TypedDict


class CreateFileRequest(TypedDict):
    file: str
    category: str
