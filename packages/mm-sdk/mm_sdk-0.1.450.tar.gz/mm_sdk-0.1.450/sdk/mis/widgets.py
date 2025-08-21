from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl

from ..client import SDKClient, SDKResponse


class ManifestResponse(BaseModel):
    js: str = Field(alias="app.js")
    css: str = Field(alias="app.css")


class WidgetsService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_manifest(self, timeout=3) -> SDKResponse[ManifestResponse]:
        return self._client.get(
            urljoin(str(self._url), "manifest.json"), ManifestResponse, timeout=timeout,
        )
