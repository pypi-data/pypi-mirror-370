import hashlib
import hmac

from enum import Enum, IntEnum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from .client import Empty, SDKClient, SDKResponse


class ActionCode(IntEnum):
    """action_code=1 - Факт оформления заказа на сайте
       action_code=2 - Дошедший пациент записанный на анализы через сайт
       action_code=3 - Оплаченный заказ (медкнижа, справка в бассейн, профосмотр, флг, пцр ковид)"""

    PRE_RECORD = 1
    MC = 2
    PAY = 3


class ConfirmStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"


class AdmitAdRequest(BaseModel):
    uid: str = Field(description="admitad_code")
    order_id: str = Field(description="id заказа в мис")
    campaign_code: str = Field(description="одна из настроек интеграции")
    action_code: ActionCode = Field(description="Коды действий. Возможны 1/2/3.")
    tariff_code: int = Field(description="1 – Тариф по умолчанию", default=1)
    currency_code: str = Field(default="RUB")
    position_id: int = Field(description="Номер услуги в корзине")
    position_count: int = Field(description="Количество позиций в корзине")
    payment_type: str = Field(default="sale")
    product_id: str = Field(description="Код услуги")
    quantity: int = Field(description="Количество единиц услуги", default=1)
    postback: int = Field(default=1)
    postback_key: str = Field(description="Ключ авторизации")
    price: int = Field(description="Цена услуги")
    client_id: Optional[str]

    class Config:
        use_enum_values = True


class ConfirmRequest(BaseModel):
    campaign_code: str
    revision_key: str
    order_id: str
    status: ConfirmStatus
    comment: str = ""
    amount: float

    class Config:
        use_enum_values = True


class AdmitAdService:
    def __init__(self, client: SDKClient, url: HttpUrl = "https://ad.admitad.com/"):
        self._client = client
        self._url = url

    def send_position(self, query: AdmitAdRequest, timeout=3) -> SDKResponse[Empty]:
        return self._client.get(
            self._url + "r", Empty, params=query.dict(), timeout=timeout
        )

    def confirm_order(self, query: ConfirmRequest, timeout=3) -> SDKResponse[Empty]:
        campaign_code = query.campaign_code.encode("utf-8")
        order_id = query.order_id.encode("utf-8")
        revision_secret_key = query.revision_key.encode("utf-8")
        revision_sign = hmac.new(
            revision_secret_key, campaign_code + order_id, hashlib.sha1
        ).hexdigest()
        return self._client.get(
            self._url + "rp",
            Empty,
            params={
                "campaign_code": query.campaign_code,
                "revision_sign": revision_sign,
                "order_id": order_id,
                "status": query.status.value,
                "amount": query.amount,
                "comment": query.comment,
            },
            timeout=timeout,
        )
