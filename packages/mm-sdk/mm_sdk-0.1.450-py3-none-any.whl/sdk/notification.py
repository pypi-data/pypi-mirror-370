import enum
from typing import Optional, Union

from pydantic import BaseModel

from .client import HttpUrl, SDKClient, SDKResponse


class EmailConfigRequest(BaseModel):
    name: str
    host_name: str
    host_port: str
    username: str
    password: str


class EmailConfigResponse(BaseModel):
    created: str


class TelegramConfigRequest(BaseModel):
    name: str
    bot_name: str
    token: str


class TelegramConfigResponse(BaseModel):
    created: str


class NotificationConfigRequest(BaseModel):
    service: str
    notification_type: str
    email_config: Optional[int] = None
    telegram_config: Optional[int] = None


class NotificationConfigResponse(BaseModel):
    created: str
    error: Optional[str] = None


class NotificationRequest(BaseModel):
    msg: str
    receiver: str
    subject: Optional[str] = None
    service: str
    notification_type: str
    spam_countdown: Optional[int] = None  # время в секундах


class NotificationResponse(BaseModel):
    status: str
    error: Optional[str] = None


class NotificationService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url
        self._url_email_config = self._url + "api/email_config"
        self._url_telegram_config = self._url + "api/telegram_config"
        self._url_notification_config = self._url + "api/notification_config"
        self._url_notification = self._url + "api/notification"

    def create_email_config(
        self, query: EmailConfigRequest, timeout=3
    ) -> SDKResponse[EmailConfigResponse]:
        return self._client.post(
            self._url_email_config,
            response_class=EmailConfigResponse,
            data=query.json(),
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )

    def create_telegram_config(
        self, query: TelegramConfigRequest, timeout=3
    ) -> SDKResponse[TelegramConfigResponse]:
        return self._client.post(
            self._url_telegram_config,
            response_class=TelegramConfigResponse,
            data=query.json(),
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )

    def create_notification_config(
        self, query: NotificationConfigRequest, timeout=3
    ) -> SDKResponse[NotificationConfigResponse]:
        return self._client.post(
            self._url_notification_config,
            response_class=NotificationConfigResponse,
            data=query.json(),
            timeout=timeout,
        )

    def create_notification(
        self, query: NotificationRequest, timeout=3
    ) -> SDKResponse[NotificationResponse]:
        return self._client.post(
            self._url_notification,
            response_class=NotificationResponse,
            data=query.json(),
            timeout=timeout,
        )
