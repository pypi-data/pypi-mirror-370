import json
import string
from hashlib import sha256

import httpx
from pydantic import BaseModel, Field

from .resource_abc import CamelAlias, Resource, register_resource
from .urlfmt import Urlfmt

u: string.Formatter = Urlfmt("/api/api/systemconfiguration/cutlabels")

_URL_FORMAT = "{base}/{code}"


class CutTime(CamelAlias, BaseModel):
    hours: int
    minutes: int
    seconds: float


@register_resource()
class CutLabelResource(CamelAlias, BaseModel, Resource):
    id: str = Field(init=True, exclude=True)
    code: str
    display_name: str
    description: str | None = None
    cut_local_time: CutTime
    time_zone: str

    def read(self, client: httpx.Client, old_state):
        url = u.format(_URL_FORMAT, code=old_state.code)
        return client.get(url).json()

    def create(self, client: httpx.Client):
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        sorted_desired = json.dumps(desired, sort_keys=True)
        content_hash = sha256(sorted_desired.encode()).hexdigest()
        client.post(u.format("{base}"), json=desired)
        return {"code": self.code, "content_hash": content_hash}

    @staticmethod
    def delete(client: httpx.Client, old_state):
        code = old_state.code
        client.delete(u.format(_URL_FORMAT, code=code))

    def update(self, client: httpx.Client, old_state):
        if self.code != old_state.code:
            self.delete(client, old_state)
            return self.create(client)
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        sorted_desired = json.dumps(desired, sort_keys=True)
        desired_hash = sha256(sorted_desired.encode()).hexdigest()
        if desired_hash == old_state.content_hash:
            return None
        client.put(u.format(_URL_FORMAT, code=self.code), json=desired)
        return {"code": self.code, "content_hash": desired_hash}

    def deps(self):
        return []


class CutLabelRef(CamelAlias, BaseModel):
    id: str = Field(init=True, exclude=True)
    code: str

    def attach(self, client: httpx.Client):
        try:
            url = u.format(_URL_FORMAT, code=self.code)
            response = client.get(url)
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise RuntimeError(f"CutLabel {self.code} not found")
            raise
