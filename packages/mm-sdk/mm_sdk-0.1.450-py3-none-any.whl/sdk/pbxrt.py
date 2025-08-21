from .client import Empty, HttpUrl, SDKClient, SDKResponse
from pydantic import BaseModel


class MakeACallRequest(BaseModel):
    phone: str
    operator: str


class PbxRtService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url
        self.create_call_url = self._url + "mis_mm/call_back/create/"

    def create_call(self, query: MakeACallRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.post(
            self.create_call_url,
            Empty,
            data=query.json(),
            headers={
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
