from typing import List, Optional

from pydantic import BaseModel

from .client import HttpUrl, SDKClient, SDKResponse


class ResponseResult(BaseModel):
    code: str
    messageId: int


class DevinoResponse(BaseModel):
    code: str
    description: Optional[str]
    result: ResponseResult


class VkData(BaseModel):
    subject: str
    priority: str
    routes: List[str]
    validityPeriod: int
    phone: str
    templateId: str
    templateData: dict


class SendVkRequest(BaseModel):
    vk: VkData


class ViberData(BaseModel):
    subject: str
    priority: str
    validityPeriod: int
    type: str = "viber"
    contentType: str
    text: str
    dstAddress: str


class SmsData(BaseModel):
    srcAddress: str
    text: str
    validityPeriod: int
    dstAddress: str


class SendAllRequest(BaseModel):
    vk: VkData
    viber: ViberData
    sms: SmsData


class DevinoService:
    def __init__(self, client: SDKClient, url: HttpUrl, token: str):
        self.client = client
        self._url = url
        self.token = token
        self.send_vk_url = self._url + "send/vk"

    def send_vk(self, query: SendVkRequest, timeout=3) -> SDKResponse[DevinoResponse]:
        return self.client.post(
            self.send_vk_url,
            DevinoResponse,
            data=query.json(),
            headers={
                "Authorization": f"Basic {self.token}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def send_all(self, query: SendAllRequest, timeout=3) -> SDKResponse[DevinoResponse]:
        return self.client.post(
            self.send_vk_url,
            DevinoResponse,
            data=query.json(),
            headers={
                "Authorization": f"Basic {self.token}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
