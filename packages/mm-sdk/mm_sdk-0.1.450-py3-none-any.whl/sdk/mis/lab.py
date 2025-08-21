import datetime

from enum import Enum
from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl

from .. import Gender
from ..client import SDKClient, SDKResponse


class ConstraintType(str, Enum):
    REQUIRED_FIELDS = "required_fields"
    EXCLUDED_SERVICES = "excluded_services"
    REQUIRED_SERVICES = "required_services"
    PLACE = "place"
    DAY_OF_WEEK = "day_of_week"
    BUSINESS_HOURS_FOR_SERVICE = "business hours for service"


class ConstraintRequiredField(str, Enum):
    DIURESIS_FIELD = "diuresis"
    WEIGHT_FIELD = "weight"
    HEIGHT_FIELD = "height"
    PREGNANCY_WEEK_FIELD = "pregnancy_week"
    CYCLE_DAY_FIELD = "cycle_day"
    CYCLE_PHASE_FIELD = "cycle_phase"
    POST_FIELD = "post"
    WORK_PLACE_PHONE_FIELD = "work_place_phone"
    WORK_PLACE_FIELD = "work_place"
    TRIP_FIELD = "trip"
    WORK_PLACE_ADDRESS_FIELD = "work_place_address"
    TRIP_DATE_FIELD = "trip_date"
    REGISTRATION_CITY = "registration_city"
    REGISTRATION_STREET = "registration_street"
    REGISTRATION_BUILDING = "registration_building"
    REGISTRATION_QUARTER = "registration_quarter"
    PASSPORT_DATE = "passport_date"
    PASSPORT_DEPARTMENT_CODE = "passport_department_code"
    CONTINGENT_COVID = "contingent_covid"


class ConstraintsRequest(BaseModel):
    price_code: Optional[List[str]]
    type: Optional[ConstraintType]
    service_id: Optional[List[str]]

    class Config:
        use_enum_values = True


class GetCostRequest(BaseModel):
    lab_order_id: Optional[int]
    lab_service_ids: Optional[List[int]]
    price_codes: List[str]
    lab_price_id: Optional[int]


class ConstraintsResponse(BaseModel):
    id: int
    price_code: str
    type: ConstraintType
    gender: Optional[Gender]
    med_centers: Optional[List[Optional[str]]]
    excluded_days: Optional[List[Optional[int]]]
    excluded_services: Optional[List[Optional[str]]]
    required_fields: Optional[List[Optional[ConstraintRequiredField]]]
    service_start_time_in_weekdays: Optional[datetime.time]
    service_end_time_in_weekdays: Optional[datetime.time]
    service_start_time_in_weekends: Optional[datetime.time]
    service_end_time_in_weekends: Optional[datetime.time]


class PublicCostResponse(BaseModel):
    price_code: str
    cost: Optional[int]
    discount_cost: Optional[int]


class LabConstraintService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_constraints(
        self, query: ConstraintsRequest, timeout=3
    ) -> SDKResponse[List[ConstraintsResponse]]:
        return self._client.get(
            urljoin(str(self._url), "lab/rest/constraints/"),
            ConstraintsResponse,
            params=query.dict(exclude_unset=True),
            timeout=timeout,
        )


class RetailService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_public_costs(self, query: GetCostRequest = None, timeout=3) -> SDKResponse[List[PublicCostResponse]]:
        return self._client.get(
            urljoin(str(self._url), "lab/price/external/costs/"),
            PublicCostResponse,
            params=query.dict(exclude_unset=True) if query else None,
            timeout=timeout,
        )
