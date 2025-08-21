from enum import Enum
from typing import Dict, List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel

from .client import Empty, SDKClient, SDKResponse


class CashierRequest(BaseModel):
    name: str
    inn: str
    user_number: int = 29


class PayMethod(str, Enum):
    CASH = 1
    CASHLESS = 2
    COMBO = 3


class Service(BaseModel):
    name: str
    quantity: int
    department: int
    cost: int


class PayServicesRequest(BaseModel):
    pay_method: PayMethod
    services: List[Service]
    org_name: Optional[str]
    org_inn: Optional[str]
    cash: int
    cashless: int
    phone_email: Optional[str]
    tax: int = 0
    password: int = 29

    class Config:
        use_enum_values = True


class RefundServicesRequest(BaseModel):
    pay_method: PayMethod
    services: List[Service]
    org_name: Optional[str]
    org_inn: Optional[str]
    cash: Optional[int]
    cashless: Optional[int]
    phone_email: Optional[str]
    tax: int = 0
    password: int = 29

    class Config:
        use_enum_values = True


class RegisterResponse(BaseModel):
    code: str
    description: str
    number: Optional[str]  # номер операции в ОФД


class CashRegisterService:
    def __init__(self, client: SDKClient, tokens: Dict):
        self._client = client
        self._tokens = tokens

    def set_cashier(
        self, host: str, query: CashierRequest, timeout: int = 30
    ) -> SDKResponse[RegisterResponse]:
        return self._client.post(
            urljoin(self._get_url(host), "rest/set_cashier/"),
            Empty,
            json=query.dict(),
            headers=self._get_headers(host),
            timeout=timeout,
        )

    def pay_services(
        self, host, query: PayServicesRequest, timeout: int = 30
    ) -> SDKResponse[RegisterResponse]:
        return self._client.post(
            urljoin(self._get_url(host), "rest/multi_service_check/"),
            RegisterResponse,
            json=query.dict(exclude_none=True),
            headers=self._get_headers(host),
            timeout=timeout,
        )

    def refund_services(
        self, host, query: RefundServicesRequest, timeout: int = 30
    ) -> SDKResponse[RegisterResponse]:
        return self._client.post(
            urljoin(self._get_url(host), "rest/multi_service_return_sale/"),
            RegisterResponse,
            json=query.dict(exclude_none=True),
            headers=self._get_headers(host),
            timeout=timeout,
        )

    def report_x(self, host, timeout: int = 30) -> SDKResponse[RegisterResponse]:
        return self._client.post(
            urljoin(self._get_url(host), "rest/x_report/"),
            RegisterResponse,
            json={},
            headers=self._get_headers(host),
            timeout=timeout,
        )

    def report_z(self, host, timeout: int = 30) -> SDKResponse[RegisterResponse]:
        return self._client.post(
            urljoin(self._get_url(host), "rest/z_report/"),
            RegisterResponse,
            json={},
            headers=self._get_headers(host),
            timeout=timeout,
        )

    def cancel(self, host, timeout: int = 30) -> SDKResponse[RegisterResponse]:
        return self._client.post(
            urljoin(self._get_url(host), "rest/cancel_check/"),
            RegisterResponse,
            json={},
            headers=self._get_headers(host),
            timeout=timeout,
        )

    def continue_print(self, host, timeout: int = 30) -> SDKResponse[RegisterResponse]:
        return self._client.post(
            urljoin(self._get_url(host), "rest/continue_print/"),
            RegisterResponse,
            json={},
            headers=self._get_headers(host),
            timeout=timeout,
        )

    def _get_headers(self, host) -> dict:
        return {"Authorization": f"Token {self._tokens[host]}"}

    @staticmethod
    def _get_url(host) -> str:
        return f"http://{host}:8000"
