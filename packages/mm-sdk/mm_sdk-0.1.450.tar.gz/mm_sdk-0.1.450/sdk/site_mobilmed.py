import datetime
import json

from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from .client import Empty, SDKClient, SDKResponse


class Service(BaseModel):
    price_code: str
    cost: str


class ResultVisitRequest(BaseModel):
    number: int
    datetime_visit: datetime.datetime
    payment_cost: Optional[int]
    payment_date: Optional[datetime.datetime]
    client_phone: Optional[str]
    order_id: Optional[str]
    services: Optional[List[Service]]


class SiteService:
    def __init__(self, client: SDKClient, url: HttpUrl, token: str):
        self._client = client
        self._url = url
        self._token = token

    def send_result_visit(self, query: ResultVisitRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.get(
            self._url,
            Empty,
            data=json.dumps(query.dict()),
            timeout=timeout,
            headers={"Authorization": self._token},
        )
