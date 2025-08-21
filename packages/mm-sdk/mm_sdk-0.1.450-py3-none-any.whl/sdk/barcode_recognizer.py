from pathlib import Path
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl

from .client import SDKClient, SDKResponse


class BarcodeRequest(BaseModel):
    file_path: Path


class BarcodeResponse(BaseModel):
    text: str


class BarcodeRecognizeService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        assert url.endswith("/")
        self._client = client
        self._url = url

    def recognize(
        self, query: BarcodeRequest, timeout=15
    ) -> SDKResponse[BarcodeResponse]:
        files = {"filename": open(str(query.file_path), "rb")}
        return self._client.post(
            urljoin(str(self._url), "upload/"),
            BarcodeResponse,
            files=files,
            timeout=timeout,
        )
