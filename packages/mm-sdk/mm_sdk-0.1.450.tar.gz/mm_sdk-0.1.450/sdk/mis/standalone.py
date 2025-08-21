from pydantic import BaseModel

from ..client import SDKClient, SDKResponse


class LocalChangeResponse(BaseModel):
    have_local_changes: bool


class ImportRequest(BaseModel):
    name: str
    import_type: str
    path_to_dump: str
    webdav_ip_address: str
    task_id: int


class ImportResponse(BaseModel):
    success: str


class ExportRequest(BaseModel):
    name: str
    export_type: str
    task_id: int


class ExportResponse(BaseModel):
    success: str


class GetLatestDumpRequest(BaseModel):
    config: str


class GetLatestDumpResponse(BaseModel):
    zip_path: str


class MisStandAloneService:
    def __init__(self, client: SDKClient):
        self._client = client

    def have_changes(self, url, timeout=3) -> SDKResponse[LocalChangeResponse]:
        return self._client.get(url, LocalChangeResponse, timeout=timeout,)

    def import_dump(
        self, url, query: ImportRequest, timeout=5
    ) -> SDKResponse[ImportResponse]:
        return self._client.post(
            url, ImportResponse, data=query.dict(), timeout=timeout,
        )

    def export_dump(
        self, url, query: ExportRequest, timeout=5
    ) -> SDKResponse[ExportResponse]:
        return self._client.post(
            url, ExportResponse, data=query.dict(), timeout=timeout,
        )
