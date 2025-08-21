import json

from enum import Enum
from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl

from .client import Empty, SDKClient, SDKResponse


class ResultChoice(str, Enum):
    NORMAL = "NORMAL"
    NOT_NORMAL = "NOT_NORMAL"
    ORDERED = "ORDERED"


class OrderType(str, Enum):
    LMK = "lmk"
    PROF = "prof"


class MisOrderedService(BaseModel):
    service_name: str
    service_code: str
    laboratory: Optional[str]
    result: ResultChoice


class MisOrderRequest(BaseModel):
    external_id: str
    type: OrderType
    ordered_services: List[MisOrderedService]


class LisOrderedService(BaseModel):
    service_name: str
    service_code: str
    result: ResultChoice


class LisOrderRequest(BaseModel):
    external_id: str
    ordered_services: List[LisOrderedService]


class ReestrService:
    def __init__(self, client: SDKClient, url: HttpUrl, token: str):
        self._client = client
        self._url = url
        assert self._url.endswith("/")
        self._token = token

    def send_mis_order(self, query: MisOrderRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(str(self._url), "api/v1/mis_order"),
            Empty,
            data=json.dumps(query.dict()),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    def send_lis_order(self, query: LisOrderRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(str(self._url), "api/v1/lab_order"),
            Empty,
            data=json.dumps(query.dict()),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )
