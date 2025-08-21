from enum import Enum

from pydantic import BaseModel


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"


class BytesResponse(BaseModel):
    bytes: bytes


class PdfResponse(BytesResponse):
    pass


class SdkException(Exception):
    pass
