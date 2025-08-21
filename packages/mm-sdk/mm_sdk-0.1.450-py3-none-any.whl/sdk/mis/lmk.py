import datetime

from enum import Enum
from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl, validator

from ..base import PdfResponse
from ..client import Empty, SDKClient, SDKResponse


class Client(BaseModel):
    phone_number: Optional[str]
    email: Optional[str]
    last_name: str
    first_name: str
    middle_name: Optional[str]
    birth: str
    post: Optional[str] = Field(alias="job")


class Trace(BaseModel):
    uuid: str
    label: str
    dt: Optional[datetime.date]
    description: str

    @validator("dt", pre=True)
    def ignore_time(cls, value):
        if value:
            return datetime.datetime.strptime(value[:10], "%Y-%m-%d").date()
        return


class LmkTraceResponse(BaseModel):
    client: Client
    trace: List[Trace]


class Medicine(BaseModel):
    latest_date: datetime.date
    next_date: Optional[datetime.date]
    nearest_expired_date: Optional[datetime.date]
    has_admission: Optional[bool]


class Attestation(BaseModel):
    latest_date: Optional[datetime.date]
    next_date: Optional[datetime.date]
    reg_date: Optional[datetime.date]


class Lmk(BaseModel):
    reg_number: Optional[str]
    blank_number: str
    med_dat: Optional[datetime.date]
    job: str
    category: str
    type: str
    need_att: bool


class LmkError(str, Enum):
    not_all_medicine = "not_all_medicine"
    attestation_not_found = "attestation_not_found"


class LmkServiceResult(BaseModel):
    name: str
    priority: float
    result_date: Optional[datetime.date]
    expired_date: Optional[datetime.date]
    done: bool
    was: bool
    is_external: bool


class LmkDelivery(BaseModel):
    ready_date: Optional[datetime.date]
    hand_date: Optional[datetime.date]


class Order(BaseModel):
    date: datetime.date
    number: str
    mc: str


class LmkProblem(BaseModel):
    name: str
    code: str
    is_notified: bool


class CheckLmkResponse(BaseModel):
    lmk: Lmk
    medicine: Medicine
    attestation: Optional[Attestation]
    client: Client
    warnings: List[LmkError]
    problems: List[LmkProblem]
    medicine_results: Optional[List[LmkServiceResult]]
    delivery: Optional[LmkDelivery]
    last_order: Optional[Order]

    class Config:
        use_enum_values = True


class OrderTraceRequest(BaseModel):
    phone: str
    lab_number: str


class CheckLmkRequest(BaseModel):
    blank_number: str
    last_name: str
    first_name: str
    take_medicine: bool = False


class SetHandDateRequest(BaseModel):
    uuids: List[str]
    hand_date: datetime.date


class ConclusionRequest(BaseModel):
    lab_number: int


class LmkService:
    def __init__(self, client: SDKClient, url: HttpUrl = None):
        self._client = client
        self._url = url

    def order_trace(
        self, query: OrderTraceRequest, timeout=3
    ) -> SDKResponse[LmkTraceResponse]:
        return self._client.get(
            urljoin(str(self._url), "lmk/rest/order_detailed_trace_step/"),
            LmkTraceResponse,
            params=query.dict(),
            timeout=timeout,
        )

    def check_lmk(
        self, query: CheckLmkRequest, timeout=3
    ) -> SDKResponse[CheckLmkResponse]:
        return self._client.get(
            urljoin(str(self._url), "lmk/rest/check_lmk_v2/"),
            CheckLmkResponse,
            params=query.dict(),
            timeout=timeout,
        )

    def set_orders_hand_date(
        self, query: SetHandDateRequest, mis_url, timeout=3
    ) -> SDKResponse[Empty]:
        return self._client.post(
            urljoin(mis_url, "lmk/rest/orders/set_hand_date/"),
            Empty,
            data=query.dict(),
            timeout=timeout,
        )

    def conclusion_pdf(
        self, query: ConclusionRequest, timeout=30
    ) -> SDKResponse[PdfResponse]:
        return self._client.get(
            urljoin(str(self._url), f"lmk/api/conclusion/{query.lab_number}/"),
            PdfResponse,
            headers={"Content-Type": "application/pdf"},
            timeout=timeout,
        )
