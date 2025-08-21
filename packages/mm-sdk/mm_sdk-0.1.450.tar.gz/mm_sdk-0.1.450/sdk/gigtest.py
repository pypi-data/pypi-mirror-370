from datetime import date as datetime_date
from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, root_validator

from .client import Empty, SDKClient, SDKResponse


COMMON_GIGTEST_TIMEOUT = 10
LONG_GIGTEST_TIMEOUT = 60 + 2


class MedResearchType(IntEnum):
    exam = 0
    lab = 1
    func = 2
    vaccine = 3


class MedResearchBlockType(Enum):
    exam = 0
    lab = 1
    vaccine = 2


class MedBookType(IntEnum):
    paper = 0
    digital = 1


class GenderType(IntEnum):
    any = 0
    male = 1
    female = 2


class SyncStatus(str, Enum):
    awaiting_signs = "awaiting_signs"  # "Ждет подписания"
    pending = "pending"  # "Ожидает отправки"
    in_process = "in_process"  # "В процессе"
    on_check = "on_check"  # "На проверке"
    succeeded = "succeeded"  # "Отправлено"
    failed = "failed"  # "Ошибка"


class ActivityResponse(BaseModel):
    id: int = Field(description="id")
    key: str = Field(description="unique key")
    parent_id: Optional[int] = Field(description="id of parent activity")
    title: str = Field(description="unique key")


class SectionResponse(BaseModel):
    id: int = Field(description="id")
    activity_key: Optional[str] = Field(
        description="Тип деятельности из activities.key"
    )
    title: str = Field(description="Название")
    image_url: Optional[str] = Field(description="Картинка типа")
    recommended: bool = Field(description="Рекомендовано или нет")


class CountryResponse(BaseModel):
    id: int = Field(description="id")
    name: str = Field(description="Название")


class MedResearchResult(BaseModel):
    id: int = Field(description="id")
    name: str = Field(description="Название")
    key: str = Field(description="Уникальный идентификатор")
    value: int = Field(description="Значение")


class MedicalResearchResponse(BaseModel):
    id: int = Field(description="id")
    name: str = Field(description="Название")
    key: str = Field(description="Уникальный идентификатор")
    activity_keys: List[str] = Field(description="Ключи типов деятельности")
    period: Optional[int] = Field(description="Периодичность в месяцах")
    important: bool = Field(
        description="Важность исследования. В случае положительно результата, "
        "заявитель будет заблокирован"
    )
    type: MedResearchType = Field(description="Тип исследования")
    block_type: Optional[MedResearchBlockType] = Field(
        description="Тип группы исследований"
    )
    results: List[MedResearchResult] = Field(
        description="Справочник возможных" " результатов"
    )

    class Config:
        use_enum_values = True


# КЛИЕНТ
class SearchClientRequest(BaseModel):
    medbook_number: str = Field(description="Номер ЛМК")
    lastname: str = Field(description="Фамилия")


class ClientInfo(BaseModel):
    home_address: Optional[str] = Field(description="Адрес")
    phone: Optional[str] = Field(description="Телефон")
    company_name: Optional[str] = Field(description="Название организации")
    position: Optional[str] = Field(description="Должность")
    birthday: Optional[datetime_date] = Field(description="Дата рождения")


class CreateClientRequest(ClientInfo):
    fio: str = Field(description="ФИО")
    birthday: datetime_date = Field(description="Дата рождения")
    country_id: int = Field(description="Id страны по справочнику")


class UpdateClientRequest(ClientInfo):
    pass


class ClientResponse(ClientInfo):
    id: int = Field(description="Id гигтест клиента")
    birthday: Optional[str] = Field(description="Дата рождения")


# МЕДКНИЖКА
class MedicalBookRequest(BaseModel):
    number: str = Field(description="Номер ЛМК")
    regnum: str = Field(description="Рег.номер ЛМК")
    date: datetime_date = Field(description="Дата выдачи ЛМК")
    user_id: int = Field(description="Id гигтест клиента")
    activity_keys: list = Field(description="Ключи типов деятельности")
    is_elmk: Optional[MedBookType] = Field(description="Тип мед. книжки")


class UserExtended(ClientInfo):
    fio: str = Field(description="ФИО")
    birth_date: str = Field(description="Дата рождения")


class MedicalBookSearchResponseOther(BaseModel):
    id: int = Field(description="Id ЛМК в гигтесте")
    number: str = Field(description="Номер ЛМК")
    regnum: str = Field(description="Рег. номер ЛМК")
    date: str = Field(description="Дата выдачи ЛМК")
    next_education_date: str = Field(description="Дата следующей аттестации")
    status: str = Field(description="Статус ЛМК: new, accepted, returned, completed")
    activity_names: list = Field(description="Тип деятельности")
    user: UserExtended = Field(description="Гигтест клиент")
    medical_direction_ids: list = Field(description="Гигтест id мед. направлений")


class User(BaseModel):
    fio: str


class MedicalBookSearchResponse(BaseModel):
    number: str = Field(description="Номер ЛМК")
    date: str = Field(description="Дата выдачи ЛМК")
    user: User = Field(description="ФИО гигтест клиента")
    id: int = Field(description="Id ЛМК в гигтесте")


class MedicalBookResponse(BaseModel):
    id: int = Field(description="Id ЛМК в гигтесте")
    regnum: str = Field(description="Рег. номер ЛМК")


# АТТЕСТАЦИЯ
class AttestationRequest(BaseModel):
    date: datetime_date = Field(description="Дата первичной/периодической аттестации")
    section_id: int = Field(description="Id раздела")
    questions: dict = Field(description="Объект из id вопрос-ответ")
    medbook_id: Optional[int] = Field(description="Id ЛМК в гигтесте")
    medbook_number: Optional[str] = Field(description="Номер ЛМК")
    mb_regnum: str = Field(description="Рег.номер ЛМК")
    mb_date: datetime_date = Field(description="Дата выдачи ЛМК")
    attestation_number: int = Field(description="1 или 0 (первичная или периодическая)")
    user_id: int = Field(description="Id гигтест клиента")
    is_elmk: MedBookType = Field(default=MedBookType.paper, description="Тип мед. книжки")


class AttestationResponse(BaseModel):
    id: int = Field(description="Id фттестации в гигтесте")
    passed: bool = Field(description="Сдал или нет")
    result: str = Field(description="Результат")
    percent: int = Field(description="Процент сдачи")


# МЕДИЦИНА
class MedicineCreateRequest(BaseModel):
    user_id: int = Field(description="Id гигтест клиента")
    medbook_number: str = Field(description="Номер ЛМК")
    activity_key: str = Field(description="Ключи типов деятельности")
    medical_type: str = Field(
        description="Тип медосмотра (preliminary-предварительный, periodic-периодический"
    )
    direction_date: datetime_date = Field(description="Дата направления медосмотра")
    date_completion: Optional[datetime_date] = Field(
        description="Дата завершения медосмотра"
    )
    order_point: List[str] = Field(
        description="Пункт приказа 23./24./25./26. только 1 из этих"
    )


class MedicineUpdateRequest(BaseModel):
    medbook_number: str = Field(description="Номер ЛМК")
    date_completion: datetime_date = Field(description="Дата завершения медосмотра")
    results: dict = Field(description="Исследования")


class MedDirectionResultData(BaseModel):
    result_key: str = Field(description="Код исследования в гигтест")
    date_med_result: datetime_date = Field(description="Дата исследования")
    description: str = Field(description="Описание")
    self_explored: Optional[int] = Field(description="0 перенос, None проведено у нас)")


class AdditionalMedDirectionResultRequest(MedDirectionResultData):
    medical_research_key: str = Field(description="Код исследования в гигтест")
    medical_direction_id: int = Field(description="Id медобследования в гигтест")


class MedicineCreateOrUpdateResponseResults(BaseModel):
    medical_research_key: str = Field(description="Код исследования в гигтест")
    id: int = Field(description="Id медобследования в гигтест")


class MedicineCreateOrUpdateResponseResultsExtended(
    MedicineCreateOrUpdateResponseResults
):
    medical_research_name: str = Field(description="Название услуги")
    date_med_result: str = Field(description="Дата обследования")
    medical_research_result: int = Field(
        description="Результат обследования. Предположительно 1 - нет противопоказаний"
    )
    medical_research_key: str = Field(description="Код услуги по справочнику гигтест")


class MedicineCreateResponse(BaseModel):
    id: int = Field(description="Id медобследования в гигтест")
    results: List[MedicineCreateOrUpdateResponseResults] = Field(
        description="Исследования"
    )


class MedicineCreateResponseExtended(MedicineCreateResponse):
    results: List[MedicineCreateOrUpdateResponseResultsExtended] = Field(
        description="Исследования"
    )


class MedicineUpdateResponse(BaseModel):
    results: List[MedicineCreateOrUpdateResponseResults] = Field(
        description="Исследования"
    )
    sticker_links: Optional[list] = Field(description="Ссылки на исследования")


class AdditionalMedDirectionResultResponse(BaseModel):
    id: int = Field(description="Id исследования в гигтест")


# СЭМД - ПЕРЕДАЧА В РЭМД
class SignCaseRequest(BaseModel):
    sign: str = Field(description="Подпись в base64")


class DocumentInfo(BaseModel):
    local_num: str = Field(description="Уникальный номер документа")
    gigtest_num: Optional[str] = Field(
        description="Уникальный номер документа в Гигтест"
    )
    created_at: str = Field(
        description="Дата и время создания СЭМДа (Y-m-d H:M:S)"
    )
    kind: int = Field(description="Тип СЭМДа")
    description: str = Field(description="Произвольное краткое описание")
    content: str = Field(description="СЭМД в base64")


class OrganizationInfo(BaseModel):
    oid: str = Field(description="Согласно ФРМО")
    name: str = Field(description="Согласно ФРМО")


class PatientInfo(BaseModel):
    firstname: str = Field(description="Имя пациента")
    lastname: str = Field(description="Фамилия пациента")
    patrname: str = Field(description="Отчество пациента")
    birthdate: str = Field(description="Дата рождения (YYYY-MM-DD)")
    gender: GenderType = Field(description="Пол")
    snils: str = Field(description="СНИЛС")


class DoctorInfo(BaseModel):
    firstname: str = Field(description="Имя врача")
    lastname: str = Field(description="Фамилия врача")
    patrname: str = Field(description="Отчество врача")
    snils: str = Field(description="СНИЛС врача")
    position_id: int = Field(description="ID должности согласно справочнику")
    speciality_id: int = Field(description="ID специальности согласно справочнику")


class CreateCaseRequest(BaseModel):
    document: DocumentInfo = Field(description="Информация о документе")
    organization: OrganizationInfo = Field(description="Информация об организации")
    patient: PatientInfo = Field(description="Информация о пациенте")
    doctor: DoctorInfo = Field(description="Информация о враче")


class CaseError(BaseModel):
    message: str = Field(description="Сообщение об ошибке")
    description: str = Field(description="Описание ошибки")


class CaseResponse(BaseModel):
    id: int = Field(description="ID случая")
    status: SyncStatus = Field(description="Статус")
    remd_regnumber: Optional[str] = Field(description="Номер ЭМД в РЭМД")
    error: Optional[CaseError] = Field(description="Список ошибок при отправке СЭМДа")

    # в доке и примере разный ключ, `status` вместо `sync_status`
    @root_validator(pre=True)
    def accept_status_or_sync_status(cls, values):
        if 'status' not in values and 'sync_status' in values:
            values['status'] = values['sync_status']
        return values


# СОЗДАНИЕ ПАЦИЕНТА В ИЭМК
class PatientIEMK(BaseModel):
    id: int = Field(description="Внутренний идентификатор пациента")
    first_name: str = Field(description="Имя пациента")
    last_name: str = Field(description="Фамилия пациента")
    patronymic: Optional[str] = Field(None, description="Отчество пациента")
    birthday: str = Field(description="Дата рождения пациента (YYYY-MM-DD)")
    gender: GenderType = Field(description="Пол пациента")
    phone: Optional[str] = Field(None, description="Телефон пациента")
    email: Optional[str] = Field(None, description="Email пациента")


class AddressInfo(BaseModel):
    street_address_line: str = Field(description="Улица, дом и квартира")


class RegionInfo(BaseModel):
    name: str = Field(description="Название региона")


class CountryInfo(BaseModel):
    name: str = Field(description="Название страны")


class SnilsInfo(BaseModel):
    number: str = Field(description="Номер СНИЛС")


class PassportInfo(BaseModel):
    series: Optional[str] = Field(None, description="Серия паспорта")
    number: Optional[str] = Field(None, description="Номер паспорта")
    issue_org_name: Optional[str] = Field(None, description="Орган, выдавший паспорт")


class EditPatientRequest(BaseModel):
    patient: PatientIEMK = Field(description="Информация о пациенте")
    address: AddressInfo = Field(description="Адрес проживания пациента")
    region: RegionInfo = Field(description="Регион проживания пациента")
    country: CountryInfo = Field(description="Страна проживания пациента")
    snils: SnilsInfo = Field(description="СНИЛС пациента")
    passport: Optional[PassportInfo] = Field(description="Паспортные данные пациента")
    organization: OrganizationInfo = Field(description="Медицинская организация, направившая пациента")


class EditPatientResponse(BaseModel):
    message: str


class GigtestService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url
        # СПРАВОЧНИКИ
        self._get_activities_url = "/api/v2/activities"
        self._get_sections_url = "/api/v2/sections"
        self._get_countries_url = "/api/v2/countries"
        self._get_medical_researches_url = "/api/v2/medical-researches"
        # КЛИЕНТ
        self._search_client_url = "/api/v2/users/search"
        self._create_or_update_client_url = "/api/v2/users"
        # МЕДКНИЖКА
        self._medbook_url = "/api/v2/medical-books"
        self._medbook_url_search = "/api/v2/medical-books/search"
        # АТТЕСТАЦИЯ
        self._attestation_url = "/api/v2/protocols"
        # МЕДИЦИНА
        self._create_update_medicine_url = "/api/v2/medical-directions"
        self._additional_medicine_results_url = "/api/v2/medical-research-results"
        # СЭМД
        self._cases_url = "/api/v2/cases"
        self._create_patient_url = "/api/v2/cases/create-patient"
        self._update_patient_url = "/api/v2/cases/update-patient"

    # СПРАВОЧНИКИ
    def activities(self, token: str) -> SDKResponse[List[ActivityResponse]]:
        return self._client.get(
            self._full_url(self._get_activities_url, token),
            ActivityResponse,
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def sections(self, token: str) -> SDKResponse[List[SectionResponse]]:
        return self._client.get(
            self._full_url(self._get_sections_url, token),
            SectionResponse,
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def countries(self, token: str) -> SDKResponse[List[CountryResponse]]:
        return self._client.get(
            self._full_url(self._get_countries_url, token),
            CountryResponse,
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def medical_research(
        self, token: str
    ) -> SDKResponse[List[MedicalResearchResponse]]:
        return self._client.get(
            self._full_url(self._get_medical_researches_url, token),
            MedicalResearchResponse,
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    # КЛИЕНТ
    def search_client(
        self, query: SearchClientRequest, token: str
    ) -> SDKResponse[ClientResponse]:
        return self._client.get(
            self._full_url(self._search_client_url, token),
            ClientResponse,
            params=query.dict(),
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def create_client(
        self, query: CreateClientRequest, token: str
    ) -> SDKResponse[ClientResponse]:
        return self._client.post(
            self._full_url(self._create_or_update_client_url, token),
            ClientResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def update_client(
        self, query: UpdateClientRequest, client_gig_test_id: int, token: str
    ) -> SDKResponse[ClientResponse]:
        return self._client.put(
            self._full_url(
                self._create_or_update_client_url + "/" + str(client_gig_test_id), token
            ),
            ClientResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def get_client(
        self, client_gig_test_id: int, token: str
    ) -> SDKResponse[ClientResponse]:
        return self._client.get(
            self._full_url(
                self._create_or_update_client_url + "/" + str(client_gig_test_id), token
            ),
            ClientResponse,
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    # этот метод для ручного использования!
    def delete_client(self, client_gig_test_id: int, token) -> SDKResponse[Empty]:
        return self._client.delete(
            self._full_url(
                self._create_or_update_client_url + "/" + str(client_gig_test_id), token
            ),
            Empty,
            timeout=LONG_GIGTEST_TIMEOUT,
        )

    # МЕДКНИЖКИ
    def search_medbook_when_other_department(
        self, medbook_number: int, token
    ) -> SDKResponse[MedicalBookSearchResponseOther]:
        return self._client.get(
            self._full_url(self._medbook_url_search, token),
            MedicalBookSearchResponseOther,
            params={"number": medbook_number},
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def search_medbook(
        self, medbook_number: int, token: str
    ) -> SDKResponse[List[MedicalBookSearchResponse]]:
        return self._client.get(
            self._full_url(self._medbook_url, token),
            MedicalBookSearchResponse,
            params={"MedicalBooksSearch[number]": medbook_number},
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def create_medbook(
        self, query: MedicalBookRequest, token: str
    ) -> SDKResponse[MedicalBookResponse]:
        return self._client.post(
            self._full_url(self._medbook_url, token),
            MedicalBookResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def update_medbook(
        self, query: MedicalBookRequest, medbook_gig_test_id: int, token: str
    ) -> SDKResponse[MedicalBookResponse]:
        return self._client.put(
            self._full_url(self._medbook_url + "/" + str(medbook_gig_test_id), token),
            MedicalBookResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    # АТТЕСТАЦИЯ
    def create_attestation(
        self, query: AttestationRequest, token: str
    ) -> SDKResponse[AttestationResponse]:
        return self._client.post(
            self._full_url(self._attestation_url, token),
            AttestationResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def update_attestation(
        self, query: AttestationRequest, gigtest_att_id: int, token: str
    ) -> SDKResponse[AttestationResponse]:
        return self._client.put(
            self._full_url(self._attestation_url + "/" + str(gigtest_att_id), token),
            AttestationResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    # этот метод для ручного использования!
    def delete_attestation(self, gigtest_att_id: int, token: str) -> SDKResponse[Empty]:
        return self._client.delete(
            self._full_url(self._attestation_url + "/" + str(gigtest_att_id), token),
            Empty,
            timeout=LONG_GIGTEST_TIMEOUT,
        )

    # МЕДИЦИНА
    def get_med_direction(
        self, gigtest_med_direction_id: int, token: str
    ) -> SDKResponse[MedicineCreateResponseExtended]:
        return self._client.get(
            self._full_url(
                self._create_update_medicine_url + "/" + str(gigtest_med_direction_id),
                token,
            ),
            MedicineCreateResponseExtended,
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def create_med_direction(
        self, query: MedicineCreateRequest, token: str
    ) -> SDKResponse[MedicineCreateResponse]:
        return self._client.post(
            self._full_url(self._create_update_medicine_url, token),
            MedicineCreateResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def update_med_direction(
        self, query: MedicineUpdateRequest, gigtest_med_direction_id: int, token: str
    ) -> SDKResponse[MedicineUpdateResponse]:
        return self._client.put(
            self._full_url(
                self._create_update_medicine_url + "/" + str(gigtest_med_direction_id),
                token,
            ),
            MedicineUpdateResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def delete_med_direction(
        self, gigtest_med_direction_id: int, token: str
    ) -> SDKResponse[Empty]:
        return self._client.delete(
            self._full_url(
                self._create_update_medicine_url + "/" + str(gigtest_med_direction_id),
                token,
            ),
            Empty,
            timeout=LONG_GIGTEST_TIMEOUT,
        )

    # TODO выше метод get_med_direction объединить с этим, проверив апи
    def search_med_direction(
        self, gigtest_med_direction_id: int, token: str
    ) -> SDKResponse[MedicineUpdateResponse]:
        return self._client.get(
            self._full_url(
                self._create_update_medicine_url + "/" + str(gigtest_med_direction_id),
                token,
            ),
            MedicineUpdateResponse,
            timeout=COMMON_GIGTEST_TIMEOUT,
        )

    def delete_med_direction_result(
        self, gigtest_med_direction_result_id: int, token: str
    ) -> SDKResponse[Empty]:
        return self._client.delete(
            self._full_url(
                self._additional_medicine_results_url
                + "/"
                + str(gigtest_med_direction_result_id),
                token,
            ),
            Empty,
            timeout=LONG_GIGTEST_TIMEOUT,
        )

    def add_additional_result_to_med_direction(
        self, query: AdditionalMedDirectionResultRequest, token: str
    ) -> SDKResponse[AdditionalMedDirectionResultResponse]:
        return self._client.post(
            self._full_url(self._additional_medicine_results_url, token),
            AdditionalMedDirectionResultResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    # СЭМД
    def create_case(
        self, query: CreateCaseRequest, token: str
    ) -> SDKResponse[List[CaseResponse]]:
        return self._client.post(
            self._full_url(self._cases_url, token),
            CaseResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def sign_case(
        self, case_id: int, query: SignCaseRequest, token: str
    ) -> SDKResponse[List[CaseResponse]]:
        return self._client.post(
            self._full_url(f"{self._cases_url}/{case_id}/sign", token),
            CaseResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def get_case(
        self, case_id: int, token: str
    ) -> SDKResponse[List[CaseResponse]]:
        return self._client.get(
            self._full_url(f"{self._cases_url}/{case_id}", token),
            CaseResponse,
            timeout=LONG_GIGTEST_TIMEOUT,
        )

    def create_patient(
        self, query: EditPatientRequest, token: str
    ) -> SDKResponse[EditPatientResponse]:
        return self._client.post(
            self._full_url(self._create_patient_url, token),
            EditPatientResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def update_patient(
        self, query: EditPatientRequest, token: str
    ) -> SDKResponse[EditPatientResponse]:
        return self._client.post(
            self._full_url(self._update_patient_url, token),
            EditPatientResponse,
            data=query.json(exclude_none=True),
            timeout=LONG_GIGTEST_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

    def _full_url(self, url, token):
        return f"{self._url}{url}?access-token={token}"

