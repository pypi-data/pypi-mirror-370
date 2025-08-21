import datetime
import json

from typing import List, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, Field, HttpUrl

from .client import SDKClient, SDKResponse


class SearchClientRequest(BaseModel):
    fname: Optional[str]
    lname: Optional[str]
    mname: Optional[str]
    phone: Optional[str]
    birth: Optional[datetime.date]
    discountnumber: Optional[int]


class Test(BaseModel):
    lname: str
    uuid: str
    fname: str


class Client(BaseModel):
    id: str = Field(alias="_id")
    source: Test = Field(alias="_source")


class ElkStructure(BaseModel):
    hits: List[Client]


class SearchClientResponse(BaseModel):
    hits: ElkStructure


class ElkService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        assert url.endswith("/")
        self._client = client
        self._url = url

    def search_client(
        self, query: SearchClientRequest, timeout=15
    ) -> SDKResponse[SearchClientResponse]:
        query_search = []
        if query.fname:
            query_search.append(f"fname:{query.fname}~")
        if query.lname:
            query_search.append(f"lname:{query.lname}~")
        if query.mname:
            query_search.append(f"mname:{query.mname}~")
        if query.phone:
            query_search.append(f"canonicalphone:{query.phone}~")
        if query.birth:
            query_search.append(f"birth:{query.birth}")
        if query.discountnumber:
            query_search.append(f"discountnumber:{query.discountnumber}~")
        return self._client.get(
            urljoin(str(self._url), "client/_search/"),
            SearchClientResponse,
            data=json.dumps(
                {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "query_string": {
                                        "query": " AND ".join(query_search),
                                        "fuzzy_prefix_length": 0,
                                        "fuzziness": "AUTO",
                                        "fuzzy_transpositions": True,
                                        "fuzzy_max_expansions": 100,
                                    }
                                }
                            ]
                        }
                    }
                }
            ),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
