from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl

from ..client import Empty, SDKClient, SDKResponse


class CallBackRequest(BaseModel):
    task_id: str
    data: str
    has_error: bool


class MisSamdService:
    def __init__(self, client: SDKClient):
        self._client = client

    def send_callback(
        self, query: CallBackRequest, url: HttpUrl, timeout=3
    ) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(str(url), "samd/tasks/callback/"),
            Empty,
            json=query.dict(exclude_none=True),
            timeout=timeout,
        )
