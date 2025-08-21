from urllib.parse import urljoin

from pydantic import BaseModel

from .client import Empty, SDKClient, SDKResponse


class NoteStatusRequest(BaseModel):
    ip: str
    have_local_changes: bool


class NoteLogRequest(BaseModel):
    task: int
    status: str
    description: str


class NoteMasterService:
    def __init__(self, client: SDKClient):
        self._client = client

    def status(
        self, base_url: str, query: NoteStatusRequest, timeout=3
    ) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(base_url, "status/"), Empty, data=query.dict(), timeout=timeout,
        )

    def create_log(
        self, base_url: str, query: NoteLogRequest, timeout=3
    ) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(base_url, "log/"), Empty, data=query.dict(), timeout=timeout
        )
