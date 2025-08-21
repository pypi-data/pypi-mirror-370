import datetime

from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, HttpUrl

from ..client import Empty, SDKClient, SDKResponse


class UserRequest(BaseModel):
    username: str


class OrgRequest(BaseModel):
    ids: Optional[List[int]]
    name: Optional[str]


class OrgResponse(BaseModel):
    id: int
    name: str
    base_org_id: Optional[int]


class OrgResponsePaginated(BaseModel):
    results: List[OrgResponse]
    count: int
    next: Optional[str]
    previous: Optional[str]
    page_size: int


class MobilOrgService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_orgs_by_user(
        self, query: UserRequest, timeout=3
    ) -> SDKResponse[OrgResponse]:
        return self._client.get(
            urljoin(str(self._url), "mobil/api/org_by_user/"),
            OrgResponse,
            params=query.dict(),
            timeout=timeout,
        )

    def get_orgs(
        self, query: OrgRequest, timeout=3
    ) -> SDKResponse[OrgResponsePaginated]:
        return self._client.get(
            f"{self._url}/mobil/rest/external_orgs/",
            OrgResponsePaginated,
            timeout=timeout,
            params=query.dict(exclude_unset=True),
            headers={"Content-Type": "application/json"},
        )


class GetManagerRequest(UserRequest):
    name: str


class GetManagerResponse(BaseModel):
    username: str
    name: str
    email: Optional[str]
    groups: List[str] = []
    is_active: bool


class ManagerService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def get_superuser_managers(
        self, query: GetManagerRequest, timeout=3
    ) -> SDKResponse[GetManagerResponse]:
        return self._client.get(
            urljoin(str(self._url), "mobil/api/user/search/"),
            GetManagerResponse,
            params=query.dict(),
            timeout=timeout,
        )


class ClientMedicineRequest(BaseModel):
    external_id: Optional[str]
    snils: Optional[str]


class Medicine(BaseModel):
    name: str
    date: datetime.date
    expired_date: Optional[datetime.date]


class ProfInfo(BaseModel):
    number: int
    type: str
    result: str
    prp: bool


class CertificateInfo(BaseModel):
    number: int
    conclusion: bool


class ClientMedicineResponse(BaseModel):
    medicine: Optional[List[Medicine]] = []
    certificate: Optional[CertificateInfo] = None
    prof: Optional[ProfInfo] = None


class ClientMedicineService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def medicine_info(
        self, query: ClientMedicineRequest, timeout=15
    ) -> SDKResponse[ClientMedicineResponse]:
        return self._client.get(
            urljoin(str(self._url), "mobil/api/client/medicine/"),
            ClientMedicineResponse,
            params=query.dict(),
            timeout=timeout,
        )


class DeliveryOrderRequest(BaseModel):
    on_delivery: bool
    date_from: datetime.date
    date_to: datetime.date
    orgs: Optional[List[int]] = []
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    out_isnull: Optional[bool]
    delivery_status: Optional[str]
    manager_ids: Optional[List[int]] = []
    page: Optional[int]
    page_size: Optional[int]


class DeliveryDetail(BaseModel):
    way: str
    delivery_wait: Optional[str]
    delivery_date: Optional[str]
    address: Optional[str]
    itinerary: Optional[str]


class MedCenterInfo(BaseModel):
    name: str
    address: str
    metro: str


class DeliveryOrder(BaseModel):
    lmk: Optional[DeliveryDetail] = None
    certificate: Optional[DeliveryDetail] = None
    prof: Optional[DeliveryDetail] = None
    client_fio: str
    client_birth: str
    date: str
    med_center: MedCenterInfo
    org_name: str
    org_id: int
    lab_number: Optional[int]


class DeliveryOrderResponse(BaseModel):
    results: Optional[List[DeliveryOrder]] = []
    count: int
    next: Optional[str]
    previous: Optional[str]
    page_size: int


class DeliveryOrderService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url

    def delivery_info(
        self, query: DeliveryOrderRequest, timeout=15
    ) -> SDKResponse[DeliveryOrderResponse]:
        return self._client.get(
            urljoin(str(self._url), "mobil/api/order/delivery/"),
            DeliveryOrderResponse,
            params=query.dict(),
            timeout=timeout,
        )


class UpdateCodeUnitRequest(BaseModel):
    uuid: str
    code_unit: str


class MobilOrderService:
    def __init__(self, client: SDKClient) -> None:
        self._client = client

    def update_code_unit(
        self, url: str, query: UpdateCodeUnitRequest, timeout=3
    ) -> SDKResponse[Empty]:
        return self._client.patch(
            urljoin(url, f"/mobil/api/mobil_order/{query.uuid}/update_code_unit/"),
            Empty,
            data={"code_unit": query.code_unit},
            timeout=timeout,
        )
