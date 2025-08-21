from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl

from .client import Empty, SDKClient


class AdditionalFields(BaseModel):
    mc_code: str
    pre_record_number: Optional[str]


class Product(BaseModel):
    id: str
    name: str
    quantity: int = 1
    price: int


class Order(BaseModel):
    id: str
    name: str
    date_create: str
    status: str = "1"  # взял из примера, нет описания что такое статус
    price: str
    client_id: str
    roistat: Optional[str]
    additional_fields: AdditionalFields = Field(alias="fields")
    products: List[Product]


class Orders(BaseModel):
    __root__: List[Order]


class Auth(BaseModel):
    project: str
    key: str


class RoistatService:
    def __init__(self, client: SDKClient, url: HttpUrl, auth: Auth):
        assert url.endswith("/")
        self._client = client
        self._url = url
        self._auth = auth

    def add_orders(self, query: Orders, timeout: int = 3):
        return self._client.post(
            urljoin(str(self._url), "api/v1/project/add-orders"),
            Empty,
            params=self._auth.dict(),
            data=query.json(by_alias=True),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
