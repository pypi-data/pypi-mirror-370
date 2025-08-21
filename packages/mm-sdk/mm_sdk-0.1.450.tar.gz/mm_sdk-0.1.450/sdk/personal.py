from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl, SecretStr

from .base import PdfResponse
from .client import Empty, SDKClient, SDKResponse
from .pre_record import PreRecordResponse


class TokenRequest(BaseModel):
    username: str
    password: SecretStr

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class RefreshTokenRequest(BaseModel):
    refresh: str


class TokenResponse(BaseModel):
    access: str
    refresh: Optional[str]


class RegisterRequest(BaseModel):
    email: str
    phone_number: str
    password: SecretStr

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class ActivateRequest(BaseModel):
    phone: str
    code: str


class ResendSmsRequest(BaseModel):
    phone: str


class GetOrderPdf(BaseModel):
    number: str


class UserResponse(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    mis_uuid: Optional[str]
    username: str
    email: str
    phone_number: str
    birth: Optional[str]
    is_active: bool


class OrderResponse(BaseModel):
    lab_number: str
    pre_record_number: Optional[str]
    create_dt: str
    all_done_dt: Optional[str]
    pdf: Optional[str]


class OrdersResponse(BaseModel):
    results: List[OrderResponse]


class PreRecordsResponse(BaseModel):
    results: List[PreRecordResponse]


class PersonalService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        assert url.endswith("/")
        self._client = client
        self._url = url

    def get_token(self, query: TokenRequest, timeout=3) -> SDKResponse[TokenResponse]:
        return self._client.post(
            urljoin(str(self._url), "v1/token/"),
            TokenResponse,
            data=query.json(),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def refresh_token(
        self, query: RefreshTokenRequest, timeout=3
    ) -> SDKResponse[TokenResponse]:
        return self._client.post(
            urljoin(str(self._url), "v1/token/refresh/"),
            TokenResponse,
            data=query.json(),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def register(self, query: RegisterRequest, timeout=3) -> SDKResponse[UserResponse]:
        return self._client.post(
            urljoin(str(self._url), "v1/lk/register/"),
            UserResponse,
            data=query.json(),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def me(self, token: str, timeout=3) -> SDKResponse[UserResponse]:
        return self._client.get(
            urljoin(str(self._url), "v1/lk/me/"),
            UserResponse,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

    def activate(self, query: ActivateRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(str(self._url), "v1/lk/activate/"),
            Empty,
            data=query.json(),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def orders(self, token: str, timeout=10) -> SDKResponse[OrdersResponse]:
        return self._client.get(
            urljoin(str(self._url), "v1/lk/orders/"),
            OrdersResponse,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

    def pre_records(self, token: str, timeout=10) -> SDKResponse[PreRecordsResponse]:
        return self._client.get(
            urljoin(str(self._url), "v1/lk/pre_records/"),
            PreRecordsResponse,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

    def refresh_mis_data(self, token: str, timeout=10) -> SDKResponse[UserResponse]:
        return self._client.get(
            urljoin(str(self._url), "v1/lk/refresh/"),
            UserResponse,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

    def resend_sms_code(self, query: ResendSmsRequest, timeout=10) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(str(self._url), "v1/lk/resend_sms/"),
            Empty,
            data=query.json(),
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
            },
        )

    def order_pdf(
        self, query: GetOrderPdf, token: str, timeout=10
    ) -> SDKResponse[PdfResponse]:
        return self._client.get(
            urljoin(str(self._url), f"v1/lk/{query.number}/pdf/"),
            PdfResponse,
            timeout=timeout,
            headers={
                "Content-Type": "application/pdf",
                "Authorization": f"Bearer {token}",
            },
        )
