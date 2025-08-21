from typing import cast, Optional
from ryft_sdk.client import RyftClient
from ryft_sdk.models.files.dto.files import File, Files
from ryft_sdk.models.files.req.files_req import CreateFileRequest


class FilesClient:
    def __init__(self, client: RyftClient):
        self.client = client
        self.path = "files"

    async def list(
        self,
        category: Optional[str] = None,
        ascending: Optional[bool] = None,
        limit: Optional[int] = None,
        startsAfter: Optional[str] = None,
    ) -> Files:
        return cast(
            Files,
            self.client.get(
                self.path,
                {
                    "category": category,
                    "ascending": ascending,
                    "limit": limit,
                    "startsAfter": startsAfter,
                },
            ),
        )

    async def get(self, id: str, account: Optional[str] = None) -> File:
        return cast(File, self.client.get(f"{self.path}/{id}", account=account))

    async def create(
        self, req: CreateFileRequest, account: Optional[str] = None
    ) -> File:
        return cast(
            File,
            self.client.upload_file(
                endpoint=self.path,
                file_path=req.get("file"),
                category=req.get("category"),
                account=account,
            ),
        )
