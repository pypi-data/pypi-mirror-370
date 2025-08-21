from typing import List, Optional

from pydantic import Field, BaseModel, validator

from .client import SDKClient, SDKResponse


class NsiIdentifier(BaseModel):
    identifier: str


class NsiQuery(NsiIdentifier):
    version: str
    size: int = 200


class NsiResponse(BaseModel):
    result: Optional[str]
    resultText: Optional[str] = None
    resultCode: Optional[str] = None
    total: Optional[int] = None
    data: Optional[list] = Field(alias="list")
    exception: Optional[str] = None
    message: Optional[str] = None

    @validator("data", pre=True)
    def transform_data(cls, items):
        """Преобразуем eav формат в набор полей необходимых для справочника."""
        if not isinstance(items, list):
            return items
        transformed = []
        for row in items:
            transformed_item = {}
            for column in row:
                name = column["column"].lower()
                if name == "id":
                    transformed_item["nsi_id"] = column["value"]
                else:
                    transformed_item[name] = column["value"]
            transformed.append(transformed_item)
        return transformed


class NsiVersionResponse(BaseModel):
    result: Optional[str]
    resultText: Optional[str] = None
    resultCode: Optional[str] = None
    identifier: Optional[str]
    oid: Optional[str]
    version: Optional[str]
    rowsCount: Optional[int]
    lastUpdate: Optional[str]
    approveDate: Optional[str]
    exception: Optional[str] = None
    message: Optional[str] = None


class NsiService:
    def __init__(self, client: SDKClient, token: str) -> None:
        self._client = client
        self._url_data = "https://nsi.rosminzdrav.ru/port/rest/data/"
        self._url_passport = "https://nsi.rosminzdrav.ru/port/rest/passport"
        self._token = token

    def get_data(
        self, query: NsiQuery, timeout=3
    ) -> SDKResponse[NsiResponse]:
        return self._client.get(
            self._url_data,
            NsiResponse,
            params={
                "identifier": query.identifier,
                "size": query.size,
                "userKey": self._token,
                "version": query.version,
            },
            timeout=timeout,
        )

    def check_version(
        self, query: NsiIdentifier, timeout=3
    ) -> SDKResponse[NsiVersionResponse]:
        return self._client.get(
            self._url_passport,
            NsiVersionResponse,
            params={
                "identifier": query.identifier,
                "userKey": self._token,
            },
            timeout=timeout,
        )
