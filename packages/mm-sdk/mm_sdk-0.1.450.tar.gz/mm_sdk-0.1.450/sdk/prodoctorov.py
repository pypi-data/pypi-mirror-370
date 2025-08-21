import datetime
import json

from typing import List

from pydantic import BaseModel, validator

from .client import Empty, SDKClient, SDKResponse


class Cell(BaseModel):
    dt: datetime.date
    time_start: datetime.time
    time_end: datetime.time
    free: bool

    @validator("dt")
    def format_date(cls, v):
        return v.strftime("%Y-%m-%d")

    @validator("time_start", "time_end")
    def format_time(cls, v):
        return v.strftime("%H:%M")


class Doctor(BaseModel):
    id: str
    name: str
    speciality: str
    cells: List[Cell]


class Mc(BaseModel):
    id: str
    name: str
    specialists: List[Doctor]


class SendScheduleRequest(BaseModel):
    med_centers: List[Mc]


class ProDoctorovService:
    def __init__(self, client: SDKClient, login, password):
        self._client = client
        self._login = login
        self._password = password
        self._url = "https://api.prodoctorov.ru/mis"

    def send_schedule(
        self, query: SendScheduleRequest, timeout: int = 10
    ) -> SDKResponse[Empty]:
        cells = {"data": {}}
        for mc in query.med_centers:
            cells[mc.id] = mc.name
            mc_data = cells["data"].setdefault(mc.id, {})
            for spec in mc.specialists:
                mc_data[spec.id] = {
                    "efio": spec.name,
                    "espec": spec.speciality,
                    "cells": [c.dict() for c in spec.cells],
                }
        return self._client.post(
            self._url + "/send_cells/",
            Empty,
            data={
                "login": self._login,
                "password": self._password,
                "cells": json.dumps(cells),
            },
            timeout=timeout,
        )
