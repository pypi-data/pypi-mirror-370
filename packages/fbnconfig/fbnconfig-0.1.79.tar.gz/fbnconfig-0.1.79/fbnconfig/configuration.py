from __future__ import annotations

from enum import StrEnum
from typing import Any, Dict, Union

import httpx
from pydantic import BaseModel, Field, computed_field

from .resource_abc import Ref, Resource, register_resource


class SetType(StrEnum):
    PERSONAL = "personal"
    SHARED = "shared"


@register_resource()
class SetRef(BaseModel, Ref):
    """Refer to an existing configuration set"""

    id: str = Field(None, exclude=True, init=True)
    scope: str = Field(exclude=True, init=True)
    code: str = Field(exclude=True, init=True)
    type: SetType

    def attach(self, client):
        # just check it exists
        scope = self.scope
        code = self.code
        set_type = self.type
        try:
            client.get(f"/configuration/api/sets/{set_type}/{scope}/{code}").json()
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Config set {set_type}/{scope}/{code} not found")
            else:
                raise ex


@register_resource()
class SetResource(BaseModel, Resource):
    """Manage a configuration set"""

    id: str = Field(None, exclude=True, init=True)
    scope: str = Field(exclude=True, init=True)
    code: str = Field(exclude=True, init=True)
    description: str
    type: SetType

    @computed_field(alias="id")
    def set_id(self) -> Dict[str, str]:
        return {"scope": self.scope, "code": self.code}

    def read(self, client, old_state):
        scope = self.scope
        code = self.code
        set_type = old_state.type
        return client.get(f"/configuration/api/sets/{set_type}/{scope}/{code}").json()

    def create(self, client: httpx.Client) -> Dict[str, Any]:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        client.request("post", "/configuration/api/sets", json=desired)
        return {"scope": self.scope, "code": self.code, "type": self.type}

    @staticmethod
    def delete(client, old_state):
        set_type = old_state.type
        scope = old_state.scope
        code = old_state.code
        client.request("delete", f"/configuration/api/sets/{set_type}/{scope}/{code}")

    def update(self, client, old_state) -> Dict[str, Any] | None:
        if [old_state.scope, old_state.code, old_state.type] != [self.scope, self.code, self.type]:
            raise RuntimeError("Cannot change the scope, code or type on a config set")
        remote = self.read(client, old_state)
        assert remote is not None
        current = {"description": remote["description"]}
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        desired.pop("id")
        desired.pop("type")
        if desired == current:
            return None
        client.put(f"/configuration/api/sets/{self.type}/{self.scope}/{self.code}", json=desired)
        return {"scope": self.scope, "code": self.code, "type": self.type}

    def deps(self):
        return []


@register_resource()
class ItemRef(BaseModel, Ref):
    """Reference an existing configuration item with a set"""

    id: str = Field(None, exclude=True, init=True)
    set: SetRef | SetResource
    key: str
    ref: str = Field(None, exclude=False, init=False)

    def attach(self, client):
        set_type = self.set.type
        scope = self.set.scope
        code = self.set.code
        key = self.key
        try:
            get = client.get(f"/configuration/api/sets/{set_type}/{scope}/{code}/items/{key}")
            self.ref = get.json()["ref"]
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError("Config item not found")
            else:
                raise ex


class ValueType(StrEnum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    TEXTCOLLECTION = "textCollection"
    NUMBERCOLLECTION = "numberCollection"


@register_resource()
class ItemResource(BaseModel, Resource):
    """Manage a configuration item with a set"""

    id: str = Field(None, exclude=True, init=True)
    set: SetRef | SetResource = Field(exclude=True, init=True)
    key: str
    ref: str = Field(None, exclude=False, init=False)
    value: Any
    value_type: ValueType
    is_secret: bool
    description: str
    block_reveal: bool = False

    def read(self, client, old_state):
        set_type = old_state.type
        scope = old_state.scope
        code = old_state.code
        key = old_state.key
        return client.get(f"/configuration/api/sets/{set_type}/{scope}/{code}/items/{key}").json()

    def create(self, client):
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        set_type = self.set.type
        scope = self.set.scope
        code = self.set.code
        post = client.post(f"/configuration/api/sets/{set_type}/{scope}/{code}/items", json=desired)
        match = next((item for item in post.json()["items"] if item["key"] == self.key), None)
        if match is None:
            raise RuntimeError("Something wrong creating config item")
        self.ref = match["ref"]
        return {"scope": scope, "code": code, "type": set_type, "key": self.key}

    @staticmethod
    def delete(client, old_state):
        set_type = old_state.type
        scope = old_state.scope
        code = old_state.code
        key = old_state.key
        client.delete(f"/configuration/api/sets/{set_type}/{scope}/{code}/items/{key}")

    def update(self, client, old_state):
        set_type = self.set.type
        scope = self.set.scope
        code = self.set.code
        key = self.key
        # if the location has changed we remove the old one
        if [old_state.scope, old_state.code, old_state.type] != [scope, code, set_type]:
            self.delete(client, old_state)
            return self.create(client)
        remote = self.read(client, old_state)
        # can't update these using PUT
        if self.is_secret != remote["isSecret"] or self.value_type != remote["valueType"]:
            self.delete(client, old_state)
            return self.create(client)
        self.ref = remote["ref"]
        current = {k: v for k, v in remote.items() if k in ["description", "value", "blockReveal"]}
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        desired = {k: v for k, v in desired.items() if k in ["description", "value", "blockReveal"]}
        if desired == current:
            return None
        client.put(f"/configuration/api/sets/{set_type}/{scope}/{code}/items/{key}", json=desired)
        return {"scope": scope, "code": code, "type": set_type, "key": self.key}

    def deps(self):
        return [self.set]


@register_resource()
class SystemConfigResource(BaseModel, Resource):
    """Manage a system configuration item

     The default value is used to reset the system configuration value when the resource is deleted

    Example
    -------
        >>> from fbnconfig import Deployment
        >>> from fbnconfig.configuration import SystemConfigResource
        >>> validate_instruments = SystemConfigResource(
        >>>      id="validate-instr",
        >>>      code="TransactionBooking",
        >>>      key="ValidateInstruments",
        >>>      value=True,
        >>>      description="Test from fbnconfig",
        >>>      default_value=False)
        >>> Deployment("myDeployment", [validate_instruments])

    Attributes
    ----------
    id : str
      Resource identifier; this will be used in the log to reference the item resource
    code : str
      Code of the system configuration set; System configurations exist in the 'system' scope
    key: str
        Key of the set to use
    value: Any
        Configuration item value
    default_value: Any
      The value this configuration item will be set to when the resource is deleted
    """

    id: str = Field(None, exclude=True, init=True)
    code: str = Field(None, exclude=True, init=True)
    key: str
    value: str
    default_value: Any = Field(None, exclude=True, init=True)
    description: str
    block_reveal: bool = False

    def read(self, client, old_state):
        code = old_state.code
        key = old_state.key
        get = client.get(f"/configuration/api/sets/system/{code}/items/{key}")
        return get.json()["values"][0]

    def create(self, client):
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        result = client.put(
            f"/configuration/api/sets/shared/system/{self.code}/items/{self.key}", json=desired
        )
        if result is None:
            raise RuntimeError("Something wrong creating config item")
        return {"code": self.code, "key": self.key, "default_value": self.default_value}

    @staticmethod
    def delete(client, old_state):
        if old_state.default_value is None:
            pass  # can't delete system config, using default values as deleted instead
        else:
            desired = {"value": old_state.default_value}
            client.put(
                f"/configuration/api/sets/shared/system/{old_state.code}/items/{old_state.key}",
                json=desired,
            )

    def update(self, client, old_state) -> Union[None, Dict[str, Any]]:
        code = self.code
        key = self.key

        if self.key != old_state.key or code != old_state.code:
            self.delete(client, old_state)
            return self.create(client)

        remote = self.read(client, old_state)
        current = {k: v for k, v in remote.items() if k in ["description", "value", "blockReveal"]}
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        desired = {k: v for k, v in desired.items() if k in ["description", "value", "blockReveal"]}
        if desired == current:
            return None
        client.put(f"/configuration/api/sets/shared/system/{code}/items/{key}", json=desired)
        return {"code": code, "key": self.key, "default_value": self.default_value}

    def deps(self):
        return []
