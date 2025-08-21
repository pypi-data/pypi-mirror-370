import datetime

from enum import IntEnum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .base import PdfResponse
from .client import Empty, HttpUrl, SDKClient, SDKResponse


class OrderType(IntEnum):
    lmk = 0
    prof = 1
    lab = 2
    cert = 3


class ExamType(IntEnum):
    preliminary = 1
    periodical = 2


class Payment(IntEnum):
    self_pay = 1  # платит клиент
    org_pay = 2  # платит организация


class HealthGroup(IntEnum):
    first = 1
    second = 2
    third = 3


class NsiMap(BaseModel):
    code: str
    name: str


class Factor(BaseModel):
    code_29n: str  # nsi_id now


class FiasAddress(BaseModel):
    ao_guid: str
    house_guid: Optional[str] = None

    class Config:
        use_enum_values = True


class Address(BaseModel):
    full: str
    state_code: str
    postal_code: Optional[str] = None
    fias: Optional[FiasAddress] = None

    class Config:
        use_enum_values = True


class AddPatientRequest(BaseModel):
    uuid: str
    fname: str
    mname: Optional[str]
    lname: str
    birth: datetime.date
    sex: str

    passport_type: Optional[str]
    passport_number: Optional[str]
    passport_series: Optional[str]
    passport_date: Optional[datetime.date]
    passport_department_code: Optional[str]

    snils: str

    phone: Optional[str]
    email: Optional[str]

    quarter: Optional[str]
    building: Optional[str]
    city: Optional[str]
    street: Optional[str]

    registration_quarter: Optional[str]
    registration_building: Optional[str]
    registration_city: Optional[str]
    registration_street: Optional[str]
    mc_id: int

    @property
    def full_address(self):
        return " ".join(
            a
            for a in [
                self.city,
                self.street,
                self.building,
                self.quarter,
            ]
            if a
        )

    @property
    def registration_address(self):
        return " ".join(
            a
            for a in [
                self.registration_city,
                self.registration_street,
                self.registration_building,
                self.registration_quarter,
            ]
            if a
        )


class MedCenter(BaseModel):
    id: str
    license: str
    license_registration: Optional[str]
    ogrn: str
    okpo: str
    legalname: str
    phone: str
    legaladdress: str
    zip_code: str
    email: str


class Lmk(BaseModel):
    number: Optional[str] = None
    is_preliminary: bool


class Order(BaseModel):
    number: str
    exams_start: datetime.datetime
    exams_done: datetime.datetime
    next_date: datetime.date
    org_name: Optional[str]
    org_inn: Optional[str]
    post: Optional[str] = None
    factors: List[Factor]
    payment: Optional[Payment]
    code_unit: str = ""
    conclusion: Optional[str] = None
    exam_type: Optional[ExamType]
    health_group: Optional[HealthGroup]
    lmk: Optional[Lmk]
    elmk_number: Optional[str] = None

    class Config:
        use_enum_values = True


class Doctor(BaseModel):
    mis_id: str
    lname: str
    fname: str
    mname: Optional[str]
    snils: Optional[str]
    address: Optional[Address]
    speciality: Optional[str]
    post: Optional[str]
    position: Optional[NsiMap]

    class Config:
        use_enum_values = True


class Exam(BaseModel):
    conclusion: str
    date: datetime.date
    doctor: Doctor
    id: str
    nsi_id: Optional[str] = None


class LabService(BaseModel):
    date: datetime.date
    result: Optional[str]
    name: str
    id: str
    nsi_id: Optional[str] = None


class FuncDiag(BaseModel):
    date: datetime.date
    conclusion: str
    name: str
    id: str
    nsi_id: Optional[str] = None


class Vaccine(BaseModel):
    name: str
    step: Optional[str] = None
    date: datetime.date
    is_revac: bool = False
    nsi_id: Optional[str] = None


class Infection(BaseModel):
    year: int
    mkb: str


class AddMedRecordRequest(BaseModel):
    mc_id: int
    order_type: OrderType
    order: Order
    creation_date: datetime.datetime  # lmk - order_time / prof - exams_start
    patient: AddPatientRequest
    author: Doctor
    exams: List[Exam] = []
    lab_services: List[LabService] = []
    functional_diagnostics: List[FuncDiag] = []
    vaccinations: List[Vaccine] = []
    infections: List[Infection] = []
    samd_type: Literal["103", "194", "230"] = Field(
        description="Доступные типы документов samd"
    )

    class Config:
        use_enum_values = True


class SamdResponse(BaseModel):
    task_id: str


class SamdPDFRequest(BaseModel):
    task_id: Optional[int] = None
    order_number: Optional[str] = ""


class SamdService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url
        self.add_patient_url = self._url + "/api/patient/"
        self.add_med_record_url = self._url + "/api/med_record/"

    def add_patient(self, query: AddPatientRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.post(
            self.add_patient_url,
            SamdResponse,
            data=query.json(),
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )

    def add_med_record(
        self, query: AddMedRecordRequest, timeout=3
    ) -> SDKResponse[Empty]:
        return self._client.post(
            self.add_med_record_url,
            SamdResponse,
            data=query.json(),
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )

    def med_record_pdf(
        self, query: SamdPDFRequest, timeout=3
    ) -> SDKResponse[Union[PdfResponse, Empty]]:
        return self._client.get(
            self._url + "api/med_record/pdf/",
            PdfResponse,
            params=query.dict(),
            headers={"Content-Type": "application/pdf"},
            timeout=timeout,
        )
