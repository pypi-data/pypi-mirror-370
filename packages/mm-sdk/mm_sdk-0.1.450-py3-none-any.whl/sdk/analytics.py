import json

from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from sdk import Gender

from .client import Empty, SDKClient, SDKResponse


class Service(BaseModel):
    name: str
    price_code: str
    cost: str


class Client(BaseModel):
    uuid: str
    fio: str
    sex: str
    birth: str
    phone: Optional[str]
    email: Optional[str]
    nationality: Optional[str]
    city: Optional[str]
    okrug: Optional[str]
    street: Optional[str]
    building: Optional[str]
    google_cid: Optional[str]
    yandex_cid: Optional[str]


class LabOrderRequest(BaseModel):
    lab_number: str
    dc: str
    cost: str
    pre_record_number: Optional[str]
    mc_id: str
    client: Client
    services: List[Service]


class TopFive(BaseModel):
    price_code: str
    name: str


class PopServiceResponse(BaseModel):
    price_code: str
    top_five: List[TopFive]


class PriceCodeRequest(BaseModel):
    price_code: Optional[str]


class RecommendationRequest(BaseModel):
    price_code: List[str]
    sex: Optional[Gender]
    age: Optional[int]

    class Config:
        use_enum_values = True


class RecommendationService(BaseModel):
    price_code: str
    name: str


class RecommendationServiceResponse(BaseModel):
    recommendations: List[RecommendationService]


class RecommendationComplex(BaseModel):
    name: str
    services: List[RecommendationService]


class RecommendationComplexResponse(BaseModel):
    recommendations: List[RecommendationComplex]


class AnalyticsService:
    def __init__(self, client: SDKClient, url: HttpUrl, token: str):
        self._client = client
        self._url = url
        self._token = token

    def send_lab_order(self, query: LabOrderRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.post(
            self._url + "api/rfm/edit",
            Empty,
            data=json.dumps(query.dict()),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    def top_services(
        self, query: PriceCodeRequest, timeout=3
    ) -> SDKResponse[List[PopServiceResponse]]:
        return self._client.get(
            self._url + f"api/recommend/top_five",
            PopServiceResponse,
            params=query.dict(),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    def recommendations(
        self, query: RecommendationRequest, timeout=3
    ) -> SDKResponse[List[RecommendationServiceResponse]]:
        return self._client.get(
            self._url + f"api/recommend/recommendations",
            RecommendationServiceResponse,
            params=query.dict(exclude_none=True),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )

    def recommendations_v2(
        self, query: RecommendationRequest, timeout=3
    ) -> SDKResponse[List[RecommendationComplexResponse]]:
        return self._client.get(
            self._url + f"api/recommend/v2/recommendations",
            RecommendationComplexResponse,
            params=query.dict(exclude_none=True),
            timeout=timeout,
            headers={"Authorization": f"Bearer {self._token}"},
        )
