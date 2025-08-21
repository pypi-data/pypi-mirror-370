import io

from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from .client import Empty, SDKClient, SDKResponse


class FaceDetectorDetectRequest(BaseModel):
    external_id: str
    file: bytes
    file_name: str


class FindSimilarFaceRequest(BaseModel):
    file_name: str
    file: bytes


class FindSimilarFaceResponse(BaseModel):
    external_id: str
    distance: float
    comment: Optional[str]
    image: Optional[bytes]


class FaceDetectorService:
    def __init__(self, client: SDKClient, url: HttpUrl, token: str):
        self._client = client
        self._token = token
        self._url = url
        self._url_detect = self._url + "api/get_face_descriptor/"
        self._url_similar = self._url + "api/find_similar/"

    def detect(self, query: FaceDetectorDetectRequest, timeout=3) -> SDKResponse[Empty]:
        file = {"image": (query.file_name, io.BytesIO(query.file))}
        headers = {"Authorization": f"Token {self._token}"}
        return self._client.post(
            self._url_detect,
            Empty,
            data={"external_id": query.external_id},
            files=file,
            timeout=timeout,
            headers=headers,
        )

    def find_similar(
        self, query: FindSimilarFaceRequest, timeout=3
    ) -> SDKResponse[List[FindSimilarFaceResponse]]:
        file = {"image": (query.file_name, io.BytesIO(query.file))}
        headers = {"Authorization": f"Token {self._token}"}
        return self._client.post(
            self._url_similar,
            FindSimilarFaceResponse,
            files=file,
            timeout=timeout,
            headers=headers,
        )
