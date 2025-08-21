from pydantic import BaseModel, HttpUrl

from .client import Empty, SDKClient, SDKResponse


class SendSmsRequest(BaseModel):
    source_address: str = "mobilmed"
    destination_address: str
    message: str


class SmsService:
    def __init__(self, client: SDKClient, url: HttpUrl, token: str):
        self._client = client
        self._url = url
        self._token = token

    def send_sms(self, query: SendSmsRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.post(
            self._url + "send/",
            Empty,
            json=query.dict(),
            timeout=timeout,
            headers={"Authorization": f"TokenService {self._token}"},
        )
