import datetime

from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl

from .. import Gender
from ..client import SDKClient, SDKResponse
from ..pre_record import OrderResults, Service


MC_URL_BY_ID = {
    1: "https://sm.mm/",
    2: "https://dm.mm/",
    3: "https://tm.mm/",
    4: "https://fm.mm/",
}


class GetClient(BaseModel):
    uuid: str


class SearchClient(BaseModel):
    uuid: Optional[str]
    phone: Optional[str]
    ignore_lab_number: Optional[str] = Field(
        description="Для проверки has_retail можем надо исключать текущий лаб номер если у нас редактирование заявки"
    )
    has_retail: Optional[bool] = Field(
        description="Фильтрация клиентов по наличию у них розничной лаб. заявки"
    )


class Client(BaseModel):
    uuid: str
    phone: str
    last_name: str = Field(alias="lname")
    first_name: str = Field(alias="fname")
    middle_name: Optional[str] = Field(alias="mname", default="")
    birth: datetime.date
    email: Optional[str]
    sex: Gender

    class Config:
        use_enum_values = True


class ClientResultsRequest(BaseModel):
    client_uuid: str
    mc_id: int
    pre_record_number: int
    lab_number: int


class ClientResultsResponse(BaseModel):
    lab_results_url: Optional[str]
    covid_results_url: Optional[str]
    flg_results_url: Optional[str]


class ClientLabOrderResponse(BaseModel):
    number: int
    phone: str
    services: List[Service]
    lname: str
    fname: str
    mname: str
    birth: Optional[datetime.date]
    client_uuid: Optional[str]
    email: Optional[str]
    results: OrderResults
    dc: datetime.datetime


class ClientLabOrderRequest(BaseModel):
    with_pre_record: bool = False
    client_uuid: str


class ClientService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_client(self, query: GetClient, timeout=3) -> SDKResponse[Client]:
        return self._client.get(
            urljoin(str(self._url), f"mobil/rest/client/{query.uuid}/"),
            Client,
            timeout=timeout,
        )

    def search(self, query: SearchClient, timeout=3) -> SDKResponse[List[Client]]:
        return self._client.get(
            urljoin(str(self._url), "mobil/rest/client/"),
            Client,
            params=query.dict(exclude_none=True),
            timeout=timeout,
        )

    def get_results(
        self, query: ClientResultsRequest, timeout=3
    ) -> SDKResponse[ClientResultsResponse]:
        params = {
            "lab_number": query.lab_number,
            "pre_record_number": query.pre_record_number,
        }
        return self._client.get(
            urljoin(
                MC_URL_BY_ID[query.mc_id], f"mobil/client/{query.client_uuid}/results/"
            ),
            ClientResultsResponse,
            params=params,
            timeout=timeout,
        )

    def get_lab(
        self, query: ClientLabOrderRequest, timeout=3
    ) -> SDKResponse[List[ClientLabOrderResponse]]:
        return self._client.get(
            urljoin(str(self._url), f"mobil/client/{query.client_uuid}/lab_results/"),
            ClientLabOrderResponse,
            params={"with_pre_records": query.with_pre_record},
            timeout=timeout,
        )
