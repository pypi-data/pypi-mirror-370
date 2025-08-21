from typing import Any

from pydantic import BaseModel, HttpUrl

from .client import SDKClient, SDKResponse


class SignRequest(BaseModel):
    thumbprint: str
    xml_file: Any


class SignResponse(BaseModel):
    signedContent: str
    filename: str


class CryptoProService:
    def __init__(self, client: SDKClient):
        self._client = client

    def sign(
        self, query: SignRequest, token: str, url: HttpUrl, timeout=3
    ) -> SDKResponse[SignResponse]:
        return self._client.post(
            url + "signer",
            SignResponse,
            params={"thumbprint": query.thumbprint, "api-key": token},
            files={"file": query.xml_file},
            timeout=timeout,
        )
