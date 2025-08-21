import enum

from typing import List, Optional, Union
from urllib.parse import urljoin

from pydantic import BaseModel, validator

from sdk import SDKClient
from sdk.client import SDKResponse


class BalancePenalty(BaseModel):
    hour: int
    stop: int


class BalanceGroup(BaseModel):
    id: str
    penalty: BalancePenalty


class DeliveryOptions(BaseModel):
    # https://yandex.ru/routing/doc/vrp/concepts/properties-of-vehicles.html#routing-mode
    routing_mode: str = "transit"
    time_zone: str = 3
    date: str
    # https://yandex.ru/routing/d/search/?query=global_proximity_factor
    global_proximity_factor: float = 2.0
    # https://yandex.ru/routing/doc/vrp/concepts/balanced-groups.html?lang=ru
    balanced_groups: Optional[List[BalanceGroup]]


class Point(BaseModel):
    lat: float = 55.781053
    lon: float = 37.599911


class Depot(BaseModel):
    id: int = 0
    ref: str = "Новослободская 14/19с1"
    point: Point = Point()
    time_window: str = "08:00:00-20:00:00"


class StopExcessPenalty(BaseModel):
    per_stop: int = 100


class ShiftPenalty(BaseModel):
    stop_excess: StopExcessPenalty = StopExcessPenalty()


class Shift(BaseModel):
    hard_window: bool = False
    time_window: str = "08:00:00-20:00:00"
    id: str = "0"
    balanced_group_id: Optional[str]
    maximal_stops: Optional[int]
    penalty: Optional[ShiftPenalty]


class VehicleCapacity(BaseModel):
    units: int = 85


class Vehicle(BaseModel):
    id: str
    shifts: List[Shift]
    return_to_depot: bool = True
    finish_at: Optional[int]
    # https://yandex.ru/routing/doc/vrp/concepts/properties-of-vehicles.html#shift-stops
    capacity: VehicleCapacity = VehicleCapacity()
    # https://yandex.ru/routing/doc/vrp/concepts/properties-of-vehicles.html#tags
    tags: Optional[List[str]]


class ShipmentSize(BaseModel):
    units: int


class LocationType(enum.Enum):
    delivery = "delivery"
    garage = "garage"
    pickup = "pickup"


class Location(BaseModel):
    id: int
    title: str
    type: LocationType = LocationType.delivery
    time_window: str = "08:00:00-20:00:00"
    point: Point
    description: str = ""
    shipment_size: Optional[ShipmentSize]
    required_tags: Optional[List[str]]


class DeliveryRequest(BaseModel):
    depot: Depot
    vehicles: List[Vehicle]
    locations: List[Location]
    options: DeliveryOptions


class DeliveryResponse(BaseModel):
    id: str
    message: str


class Courier(BaseModel):
    company_id: int
    id: int
    name: str
    number: str
    phone: str
    sms_enabled: bool


class RouteStatus(BaseModel):
    completed: Optional[float]


class RouteDepotValue(BaseModel):
    id: int
    point: Point
    routing_mode: str
    time_window: str
    ref: str


class RouteLocationValue(BaseModel):
    id: int
    description: str
    title: str
    point: Point
    routing_mode: str
    time_window: str


class RouteNodeType(enum.Enum):
    depot = "depot"
    location = "location"


class RouteNode(BaseModel):
    type: RouteNodeType
    used_time_window: str
    value: Union[RouteLocationValue, RouteDepotValue]


class RouteLocation(BaseModel):
    node: RouteNode


class Route(BaseModel):
    run_number: int
    vehicle_id: str
    route: List[RouteLocation]


OVERLOAD_DROP_REASON = "Перегрузка"


class DroppedRoute(BaseModel):
    id: int
    drop_reason: str

    @validator("drop_reason")
    def prepare_drop_reason(cls, v):
        if "Vehicle overload" in v:
            return OVERLOAD_DROP_REASON
        return v


class RouteResult(BaseModel):
    routes: List[Route]
    vehicles: List[Vehicle]
    dropped_locations: List[DroppedRoute]


class RouteInfo(BaseModel):
    id: str
    status: RouteStatus
    message: str
    result: RouteResult


class GetRoute(BaseModel):
    id: str


class YandexCourierService:
    def __init__(
        self,
        client: SDKClient,
        delivery_token: str,
        dictionaries_token: str,
        company_id: int,
    ):
        self._client = client
        self._delivery_url = "https://courier.yandex.ru/vrs/api/v1/"
        self._dict_url = f"https://courier.yandex.ru/api/v1/companies/{company_id}/"
        self._delivery_token = delivery_token
        self._dictionaries_token = dictionaries_token

    def create_delivery(
        self, query: DeliveryRequest, timeout: int = 3
    ) -> SDKResponse[DeliveryResponse]:
        return self._client.post(
            urljoin(str(self._delivery_url), "add/mvrp"),
            response_class=DeliveryResponse,
            params={"apikey": self._delivery_token},
            data=query.json(exclude_none=True),
            timeout=timeout,
        )

    def get_delivery(self, query: GetRoute, timeout: int = 3) -> SDKResponse[RouteInfo]:
        return self._client.get(
            urljoin(str(self._delivery_url), f"result/mvrp/{query.id}"),
            response_class=RouteInfo,
            params={"apikey": self._delivery_token},
            data=query.json(),
            timeout=timeout,
        )

    def get_couriers(self, timeout=3) -> SDKResponse[List[Courier]]:
        return self._client.get(
            urljoin(str(self._dict_url), "couriers"),
            response_class=Courier,
            headers={"Authorization": f"Auth {self._dictionaries_token}"},
            timeout=timeout,
        )
