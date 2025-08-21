from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from ..client import SDKClient, SDKResponse


class Rating(str, Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    NO_DATA = "no_data"


class GetOrgInfoRequest(BaseModel):
    key: str
    inn: str


class LegalName(BaseModel):
    short: str
    full: str
    readable: str
    date: str


class ShortFull(BaseModel):
    topoShortName: str
    topoValue: str

    def full(self) -> str:
        return f"{self.topoShortName} {self.topoValue}"


class ParsedAddress(BaseModel):
    regionName: Optional[ShortFull]
    district: Optional[ShortFull]
    city: Optional[ShortFull]
    settlement: Optional[ShortFull]
    street: Optional[ShortFull]
    house: Optional[ShortFull]
    bulk: Optional[ShortFull]
    flat: Optional[ShortFull]

    def full(self) -> str:
        address_info = []
        for field, value in self.__dict__.items():
            if value is not None:
                address_info.append(value.full())
        return ", ".join(address_info)


class LegalAddress(BaseModel):
    parsedAddressRF: ParsedAddress


class UL(BaseModel):
    kpp: str
    legalName: LegalName
    legalAddress: LegalAddress


class Summary(BaseModel):
    greenStatements: Optional[bool]
    yellowStatements: Optional[bool]
    redStatements: Optional[bool]


class BriefReport(BaseModel):
    summary: Summary

    @property
    def rating(self) -> Rating:
        # указываем худший рейтинг из возможных
        if self.summary.redStatements:
            return Rating.RED
        elif self.summary.yellowStatements:
            return Rating.YELLOW
        elif self.summary.greenStatements:
            return Rating.GREEN
        else:
            return Rating.NO_DATA


class GetOrgInfoResponse(BaseModel):
    inn: str
    ogrn: str
    UL: UL
    briefReport: BriefReport


class SubscribeOrgRequestParams(BaseModel):
    key: str
    append: str


class SubscribeOrgRequestData(BaseModel):
    body: str


class SubscribeOrgResponse(BaseModel):
    ogrn: str
    inn: str


class GetChangedOrgRequest(BaseModel):
    key: str
    date: str   # Дата в формате ГГГГ-ММ-ДД


class GetChangedOrgResponse(BaseModel):
    ogrn: str


class KonturApiService:
    def __init__(self, client: SDKClient):
        self._client = client
        self._url = "https://focus-api.kontur.ru"
        self._url_req = self._url + "/api3/req"
        self._url_monList = self._url + "/api3/monList"
        self._url_mon = self._url + "/api3/req/mon"

    def get_org_info(
        self, query: GetOrgInfoRequest, timeout=3
    ) -> SDKResponse[List[GetOrgInfoResponse]]:
        return self._client.get(
            self._url_req, GetOrgInfoResponse, params=query.dict(), timeout=timeout,
        )

    def subscribe_to_updates_by_org(
        self, query_params: SubscribeOrgRequestParams, query_data: SubscribeOrgRequestData, timeout=3
    ) -> SDKResponse[List[SubscribeOrgResponse]]:
        return self._client.post(
            self._url_monList, SubscribeOrgResponse, params=query_params.dict(), data=query_data.dict(), timeout=timeout,
        )

    def get_changed_org(
        self, query: GetChangedOrgRequest, timeout=3
    ) -> SDKResponse[List[GetChangedOrgResponse]]:
        return self._client.get(
            self._url_mon, GetChangedOrgResponse, params=query.dict(), timeout=timeout,
        )
