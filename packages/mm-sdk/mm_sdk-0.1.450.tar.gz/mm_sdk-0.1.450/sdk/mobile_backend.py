import datetime
import json

from enum import Enum
from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl, root_validator

from . import Gender
from .client import Empty, SDKClient, SDKResponse


class SendTokenCodeRequest(BaseModel):
    phone: str


class AuthType(str, Enum):
    VK = "vk"
    SMS = "sms"


class TokenRequest(BaseModel):
    type: AuthType = Field(default=AuthType.SMS)
    phone: Optional[str]
    code: str

    class Config:
        use_enum_values = True

    @root_validator()
    def required_by_type(cls, values):
        auth_type = values.get("type")
        if auth_type == AuthType.SMS.value:
            raise ValueError(f"phone is required for {AuthType.SMS.value}")
        return values


class TokenResponse(BaseModel):
    token: str


class Status(BaseModel):
    label: str
    date: Optional[datetime.datetime]


class Result(BaseModel):
    created_at: datetime.datetime
    ready_at: Optional[datetime.datetime]
    result_link: Optional[HttpUrl]
    status: Status


class Subgroup(BaseModel):
    subgroup_name: str
    subgroup_id: int
    analysis: List[int]


class Analysis(BaseModel):
    analysis_id: int
    group_id: int
    analysis_type: str
    analysis_name: str
    price: int
    price_with_discount: int
    code: str
    period: str
    notice: Optional[str]
    tag: str
    description: str
    prepare: str
    cito_analysis: Optional[int]
    is_cito: bool
    bio_materials: List[str]
    med_centers: List[int]
    composition: List[int]
    results: List[Result]


class Group(BaseModel):
    group_id: int
    group_name: str
    group_type: str
    icon: Optional[HttpUrl]
    subgroups: List[int]
    analysis: List[Analysis]


class ResultsResponse(BaseModel):
    date: datetime.datetime
    number: str
    result_link: Optional[HttpUrl]
    groups: List[Group]


class ClientResponse(BaseModel):
    uuid: str
    mis_uuid: str
    last_name: str
    first_name: str
    middle_name: str
    email: Optional[str]
    phone_number: str
    birth: Optional[datetime.date]
    sex: Optional[Gender]


class ClientUpdateRequest(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    email: Optional[str]
    birth: Optional[datetime.date]
    sex: Optional[Gender]


class MobileBackendService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        assert url.endswith("/")
        self._client = client
        self._url = url

    def send_token_code(
        self, query: SendTokenCodeRequest, timeout=3
    ) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(str(self._url), "v2/auth/send_sms_code/?default_render"),
            Empty,
            data=query.json(),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def get_token(self, query: TokenRequest, timeout=3) -> SDKResponse[TokenResponse]:
        data = query.dict(exclude_none=True)
        if query.type == AuthType.SMS:
            data["code"] = int(data["code"])
        elif query.type == AuthType.VK:
            data["access_token"] = data["code"]
            del data["code"]
        return self._client.post(
            urljoin(str(self._url), "v2/auth/generate_token/?default_render"),
            TokenResponse,
            data=json.dumps(data),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def get_orders(self, token: str, timeout: int = 3) -> SDKResponse[ResultsResponse]:
        return self._client.get(
            urljoin(str(self._url), "v2/user/history/order/?default_render"),
            ResultsResponse,
            params={},
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {token}",
            },
        )

    def me(self, token: str, timeout: int = 3) -> SDKResponse[ClientResponse]:
        params = {"mis_uuid_required": True, "default_render": True}
        return self._client.get(
            urljoin(str(self._url), "v2/user/"),
            ClientResponse,
            params=params,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {token}",
            },
        )

    def update_client(
        self, query: ClientUpdateRequest, token: str, timeout: int = 3
    ) -> SDKResponse[ClientResponse]:
        return self._client.post(
            urljoin(str(self._url), "v2/user/?default_render"),
            ClientResponse,
            data=query.json(exclude_none=True),
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {token}",
            },
        )
