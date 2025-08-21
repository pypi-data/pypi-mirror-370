import datetime
import json

from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl, IPvAnyAddress, Json, root_validator

from . import Gender
from .client import SDKClient, SDKResponse


class ServiceForOrder(int, Enum):
    LAB = 5
    LMK = 4
    PROF = 3
    CERT = 1
    OUT = 6


class PaySystem(str, Enum):
    OTHER = ""  # когда наличка, не передается система оплаты
    TINKOFF_PAYMENT = "tinkoff"
    YOOKASSA_PAYMENT = "yookassa"
    # деньги платятся яндексу. Мис считает заказ полностью оплаченным
    YANDEX_PAYMENT = "yandex"


class PassportType(str, Enum):
    PASSPORT = "Паспорт гражданина РФ"
    ABROAD = "Загранпаспорт гражданина РФ"
    OTHER = "Паспорт иностранного гражданина"


class CyclePhase(str, Enum):
    FOLLICULAR = "follicular"
    OVULATORY = "ovulatory"
    LUTEAL = "luteal"
    MENOPAUSE = "menopause"
    POSTMENOPAUSE = "post_menopausal"
    PREMENOPAUSE = "premenopausal"
    NOPREGNANCY = "no pregnancy"


class CovidFields(BaseModel):
    gender: Optional[Gender]
    passport_type: Optional[PassportType]
    passport_date: Optional[datetime.date]
    passport_code: Optional[str]
    passport_series: Optional[str]
    passport_number: Optional[str]
    oms: Optional[str]
    snils: Optional[str]
    is_moscow: Optional[bool]
    registration_region: Optional[str] = ""
    registration_city: Optional[str]
    registration_street: Optional[str]
    registration_building: Optional[str] = ""
    registration_quarter: Optional[str] = ""
    fact_country: Optional[str]
    fact_republic: Optional[str]
    fact_region: Optional[str]
    fact_city: Optional[str]
    fact_street: Optional[str]
    fact_building: Optional[str]
    fact_quarter: Optional[str]
    vaccine_covid_first: Optional[datetime.date]
    vaccine_covid_first_name: Optional[str]
    vaccine_covid_second: Optional[datetime.date]
    vaccine_covid_second_name: Optional[str]

    class Config:
        use_enum_values = True


class OutData(BaseModel):
    address: str
    lat: Optional[str]
    long: Optional[str]


class LabExtraFields(BaseModel):
    gender: Optional[Gender]
    nationality: Optional[str]
    passport_type: Optional[PassportType]
    passport_date: Optional[str]
    passport_code: Optional[str]
    passport_series: Optional[str]
    passport_number: Optional[str]
    registration_city: Optional[str]
    registration_street: Optional[str]
    registration_building: Optional[str]
    registration_quarter: Optional[str]
    diuresis: Optional[str]
    weight: Optional[int]
    height: Optional[int]
    pregnancy_week: Optional[int]
    cycle_day: Optional[int]
    cycle_phase: Optional[CyclePhase]
    work_place: Optional[str]
    work_place_phone: Optional[str]
    work_place_address: Optional[str]
    trip: Optional[str]
    out: Optional[OutData]

    class Config:
        use_enum_values = True


class Source(str, Enum):
    site = "site"
    call_center = "call_center"
    delivery = "delivery"
    mobile = "mobile"


class PayType(str, Enum):
    cashless_prepayment = "cashless_prepayment"
    med_center = "med_center"
    delivery = "delivery"


class FreeDatesRequest(BaseModel):
    services: List[int]
    lab_codes: Optional[List[str]] = None
    place: int
    dt_from: datetime.datetime


class FreeTimeRequest(BaseModel):
    services: List[int]
    lab_codes: Optional[List[str]] = None
    place: int
    date: datetime.date


class GetPreRecordPlacesRequest(BaseModel):
    lab_codes: Optional[List[str]] = None


class Service(BaseModel):
    name: str
    slug: str


class WorkSchedule(BaseModel):
    week_day: int
    time_from: datetime.time
    time_to: datetime.time
    week_day_name: str


class PlacesResponse(BaseModel):
    id: int
    name: str
    med_center_id: int
    metro: str
    extra_metro: List[str]
    subnet: IPvAnyAddress
    med_center_extra_info: Union[Dict, Json]
    lat: Decimal
    lng: Decimal


class RecordTime(BaseModel):
    dt_from: datetime.datetime
    dt_to: datetime.datetime


class FreeTimeResponse(BaseModel):
    service: Service
    records: List[RecordTime]


class PreRecordRequest(BaseModel):
    service: int
    place: int
    date: datetime.date
    time: datetime.time
    birth: Optional[datetime.date]
    last_name: str
    first_name: str
    middle_name: str = ""
    client_uuid: str = ""
    operator_login: Optional[str]
    email: str
    phone: str
    analysis: List[str] = []
    source: Source = Source.site
    lab_extra_fields: Optional[LabExtraFields]
    covid_fields: Optional[CovidFields]
    pay_type: PayType = PayType.med_center
    called_from_number: Optional[str]
    operator_comment: Optional[str]
    ga_client_id: Optional[str]
    ym_client_id: Optional[str]
    admitad_code: Optional[str]
    pay_system: Optional[PaySystem]
    roistat: Optional[str]
    # игнорирую, потому что пока ненужно. Но в апи передают
    roistat_first: Optional[str]
    with_discount: bool = True
    gift_code: str = ""
    external_id: Optional[str]
    initial_cost: Optional[int]

    class Config:
        use_enum_values = True

    def convert_to_request(self):
        """Преобразовывает данные в формат, который принимает предварительная запись."""
        data = {
            "lname": self.last_name,
            "fname": self.first_name,
            "mname": self.middle_name,
            "operator_login": self.operator_login,
            "birth": self.birth.strftime("%Y-%m-%d") if self.birth else None,
            "phone": self.phone,
            "d_from": datetime.datetime.combine(self.date, self.time).strftime(
                "%Y-%m-%d %H:%M"
            ),
            "d_to": (
                datetime.datetime.combine(self.date, self.time)
                + datetime.timedelta(minutes=10)
            ).strftime("%Y-%m-%d %H:%M"),
            "place": self.place,
            "email": self.email,
            "services": [{"id": self.service}],
            "lab_services": [
                {"price_code": price_code} for price_code in self.analysis
            ],
            "source": self.source,
            "pay_type": self.pay_type,
            "with_discount": self.with_discount,
            "gift_code": self.gift_code,
            "external_id": self.external_id,
        }
        if self.initial_cost:
            data["initial_cost"] = self.initial_cost

        if self.lab_extra_fields:
            data["extra_fields"] = self.lab_extra_fields.dict(exclude_none=True)
        if self.covid_fields:
            # преобразую, в json и обратно, потому что иначе datetime остается в
            # словаре и http json дампер не переваривает
            data["covid_fields"] = json.loads(self.covid_fields.json(exclude_none=True))
        if self.called_from_number:
            data["called_from_number"] = self.called_from_number
        if self.operator_comment:
            data["operator_comment"] = self.operator_comment
        if self.ym_client_id:
            data["ym_client_id"] = self.ym_client_id
        if self.ga_client_id:
            data["ga_client_id"] = self.ga_client_id
        if self.roistat:
            data["roistat"] = self.roistat
        if self.admitad_code:
            data["admitad_code"] = self.admitad_code
        if self.pay_system:
            data["pay_system"] = self.pay_system
        if self.client_uuid:
            data["client_uuid"] = self.client_uuid
        return data


class DeliveryPreRecordRequest(BaseModel):
    birth: datetime.date
    last_name: str
    first_name: str
    middle_name: str = ""
    email: str
    phone: str
    covid_fields: CovidFields

    class Config:
        use_enum_values = True


class PreRecordTickRequest(BaseModel):
    # забрал со старого апи, это результат json.dumps() примерный набор полей
    # phone/cost/lab_services(cost/price_code
    external_data: bytes
    lmk_order_uuid: Optional[str]
    lab_order_uuid: Optional[str]
    prof_order_uuid: Optional[str]
    certificate_order_uuid: Optional[str]
    client_uuid: Optional[str]
    lname: Optional[str]
    mname: Optional[str]
    fname: Optional[str]
    birth: Optional[datetime.date]


class ClientPreRecordsRequest(BaseModel):
    client_uuid: Optional[str]
    phone: Optional[str]
    d_to: Optional[datetime.date]
    lname: Optional[str]
    services: Optional[List[ServiceForOrder]]
    limit: int = 10
    offset: int = 0

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def one_of(cls, values):
        client_uuid = values.get("client_uuid")
        phone = values.get("phone")
        if not client_uuid and not phone:
            raise ValueError("phone or client_uuid is required")
        return values


class PreRecordGetRequest(BaseModel):
    number: int
    client_uuid: Optional[str]
    phone: Optional[str]


class LabService(BaseModel):
    price_code: str


class OrderResults(BaseModel):
    lab_results_url: Optional[str]
    covid_results_url: Optional[str]
    flg_results_url: Optional[str]


class PreRecordResponse(BaseModel):
    number: int
    phone: str
    services: List[Service]
    lab_services: Optional[List[Optional[LabService]]]
    d_from: datetime.datetime
    d_to: datetime.datetime
    prepayment_is_paid: bool
    prepayment_cost: Optional[int]
    pay_type: PayType
    visit_cost: Optional[int]
    datetime_visit: Optional[datetime.datetime]
    initial_cost: Optional[int]
    pay_system: Optional[PaySystem]
    pay_service_id: Optional[str]
    med_center_id: int
    lname: str
    fname: str
    mname: str
    birth: Optional[datetime.date]
    client_uuid: Optional[str]
    email: Optional[str]
    gift_code: Optional[str]
    external_id: Optional[str]
    place: int
    extra_fields: Optional[LabExtraFields]
    covid_fields: Optional[CovidFields]
    results: Optional[OrderResults]
    dc: datetime.datetime

    class Config:
        use_enum_values = True


class PaginatedPreRecordResponse(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[PreRecordResponse]


class PreRecordDeliveryResponse(BaseModel):
    number: int


class PreRecordConfirmPayment(BaseModel):
    number: int
    pay_service_id: str
    prepayment_cost: str
    pay_system: Optional[PaySystem]

    class Config:
        use_enum_values = True


class AnalyticTags(BaseModel):
    number: int
    roistat: str
    roistat_first: Optional[str]


class EmptyResponse(BaseModel):
    pass


class PreRecordService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        assert url.endswith("/")
        self._client = client
        self._url = url

    def places(
        self, query: Optional[GetPreRecordPlacesRequest] = None, timeout=15
    ) -> SDKResponse[List[PlacesResponse]]:
        return self._client.get(
            urljoin(str(self._url), "rest/place/"),
            PlacesResponse,
            params={"lab_codes": query.lab_codes if query else None},
            timeout=timeout,
        )

    def free_dates(self, query: FreeDatesRequest, timeout=15) -> SDKResponse[list]:
        return self._client.get(
            urljoin(str(self._url), "rest/pre_record/free_dates/"),
            list,
            params={
                "services": query.services,
                "lab_codes": query.lab_codes,
                "place": query.place,
                "dt_from": query.dt_from.isoformat()[:19],
            },
            timeout=timeout,
        )

    def free_time(
        self, query: FreeTimeRequest, timeout=15
    ) -> SDKResponse[List[FreeTimeResponse]]:
        return self._client.get(
            urljoin(str(self._url), "rest/pre_record/free/"),
            FreeTimeResponse,
            params={
                "services": query.services,
                "lab_codes": query.lab_codes,
                "place": query.place,
                "date": query.date.isoformat(),
            },
            timeout=timeout,
        )

    def create_pre_record(
        self, query: PreRecordRequest, timeout=15
    ) -> SDKResponse[PreRecordResponse]:
        return self._client.post(
            urljoin(str(self._url), "rest/pre_record/"),
            PreRecordResponse,
            data=json.dumps(query.convert_to_request()),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def create_delivery_pre_record(
        self, query: DeliveryPreRecordRequest, timeout=15
    ) -> SDKResponse[PreRecordResponse]:
        """Создание предварительной записи по "доставке".
        Интеграция с анкетой на сайте mobil-med.org для ковид-пцр и яндекс доставкй
        """
        data = {
            "lname": query.last_name,
            "fname": query.first_name,
            "mname": query.middle_name,
            "birth": query.birth.strftime("%Y-%m-%d"),
            "phone": query.phone,
            "email": query.email,
            "covid_fields": json.loads(query.covid_fields.json(exclude_none=True)),
        }

        return self._client.post(
            f"{self._url}rest/pre_record_delivery/",
            PreRecordDeliveryResponse,
            data=json.dumps(data),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def update_pre_record(
        self, number, query: PreRecordRequest, timeout=15
    ) -> SDKResponse[PreRecordResponse]:
        return self._client.put(
            urljoin(str(self._url), f"rest/pre_record/{number}/"),
            PreRecordResponse,
            data=json.dumps(query.convert_to_request()),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def confirm_payment(
        self, query: PreRecordConfirmPayment, timeout=15
    ) -> SDKResponse[PreRecordResponse]:
        data = {
            "prepayment_cost": query.prepayment_cost,
            "prepayment_is_paid": True,
            "pay_service_id": query.pay_service_id,
        }
        if query.pay_system:
            data["pay_system"] = query.pay_system

        return self._client.patch(
            f"{self._url}rest/pre_record/{query.number}/",
            PreRecordResponse,
            data=json.dumps(data),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def set_analytics(
        self, query: AnalyticTags, timeout=15
    ) -> SDKResponse[PreRecordResponse]:
        return self._client.patch(
            f"{self._url}rest/pre_record/{query.number}/",
            PreRecordResponse,
            data=json.dumps({"roistat": query.roistat}),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def get_pre_record(
        self, query: PreRecordGetRequest, timeout=10, strict: bool = False
    ) -> SDKResponse[PreRecordResponse]:
        url = f"{self._url}rest/pre_record/{query.number}/"
        params = query.dict()
        del params["number"]
        if strict:
            url = f"{self._url}rest/pre_record_strict/{query.number}/"
        return self._client.get(
            url,
            PreRecordResponse,
            params=params,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    def get_client_pre_records(
        self,
        query: ClientPreRecordsRequest,
        with_pagination: bool = False,
        timeout: int = 10,
        strict: bool = False,
    ) -> SDKResponse[Union[List[PreRecordResponse], PaginatedPreRecordResponse]]:
        url = f"{self._url}rest/pre_record/"
        if strict:
            url = f"{self._url}rest/pre_record_strict/"
        resp: SDKResponse[PaginatedPreRecordResponse] = self._client.get(
            url,
            PaginatedPreRecordResponse,
            timeout=timeout,
            params=query.dict(),
            headers={"Content-Type": "application/json"},
        )
        if with_pagination:
            return resp
        else:
            # старый формат
            resp = SDKResponse[List[PreRecordResponse]](data=resp.data.results)
            return resp

    def set_tick(
        self, number: int, query: PreRecordTickRequest, timeout: int = 2
    ) -> SDKResponse[PreRecordResponse]:
        return self._client.patch(
            f"{self._url}rest/pre_record/{number}/set_tick/",
            PreRecordResponse,
            timeout=timeout,
            params=query.dict(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )
