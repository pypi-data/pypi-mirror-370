import mimetypes
import os
import requests
from typing import Any, Optional

from ryft_sdk.models.errors import RyftError
from ryft_sdk.utils import determine_base_url

from ryft_sdk._version import __version__

default_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": f"ryft-python-sdk/{__version__}",
    "ryft-sdk-name": "ryft-python-sdk",
    "ryft-sdk-version": __version__,
}


class RyftClient:
    def __init__(self, secret_key: Optional[str]):
        self.secret_key = secret_key or os.environ.get("RYFT_SECRET_KEY")
        if not self.secret_key:
            raise ValueError(
                "Secret API key is required. Please provide it as an argument or set the RYFT_SECRET_KEY environment variable."
            )

        self.base_url = determine_base_url(self.secret_key)
        self.session = requests.Session()

    def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        account: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._do("GET", endpoint, params, account=account)

    def post(
        self, endpoint: str, data: dict[str, Any], account: Optional[str] = None
    ) -> dict[str, Any]:
        return self._do("POST", endpoint, data=data, account=account)

    def patch(
        self, endpoint: str, data: dict[str, Any], account: Optional[str] = None
    ) -> dict[str, Any]:
        return self._do("PATCH", endpoint, data=data, account=account)

    def delete(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        account: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._do("DELETE", endpoint, data=data, account=account)

    def _do(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        account: Optional[str] = None,
    ) -> dict[str, Any]:
        headers = default_headers
        headers["Authorization"] = self.secret_key or ""
        if account:
            headers["Account"] = account

        self.session.headers.update(headers)

        response = {}

        if method == "GET":
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        elif method == "POST":
            response = self.session.post(f"{self.base_url}/{endpoint}", json=data)
        elif method == "PATCH":
            response = self.session.patch(f"{self.base_url}/{endpoint}", json=data)
        elif method == "DELETE":
            response = self.session.delete(f"{self.base_url}/{endpoint}", json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code < 200 or response.status_code > 299:
            raise RyftError(
                status=response.status_code,
                response=response.json(),
            )

        return response.json()

    def upload_file(
        self,
        endpoint: str,
        file_path: str,
        category: str,
        account: Optional[str] = None,
    ) -> dict[str, Any]:
        headers = default_headers
        headers["Authorization"] = self.secret_key or ""
        headers.pop("Content-Type", None)
        if account:
            headers["Account"] = account

        self.session.headers.update(headers)

        mimetypes.init()
        mimetype, _ = mimetypes.guess_type(file_path)
        if mimetype is None:
            mimetype = "application/octet-stream"

        filename = os.path.basename(file_path)

        payload = {"category": category}

        with open(file_path, "rb") as file_handle:
            files = [("file", (filename, file_handle, mimetype))]

            response = requests.request(
                "POST",
                f"{self.base_url}/{endpoint}",
                headers=headers,
                data=payload,
                files=files,
            )

            if response.status_code == 415:
                raise RyftError(
                    status=response.status_code,
                    response={
                        "message": f"Unsupported file type: {mimetype}",
                        "errors": [
                            {
                                "message": f"Unsupported file type: {mimetype}",
                                "code": "UNSUPPORTED_FILE_TYPE",
                            }
                        ],
                    },
                )

            if response.status_code < 200 or response.status_code > 299:
                raise RyftError(
                    status=response.status_code,
                    response=response.json(),
                )

            return response.json()
