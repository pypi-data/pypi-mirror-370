from __future__ import annotations

import copy
from enum import StrEnum
from typing import Any, Dict, List

import httpx
from pydantic import BaseModel, Field

from .resource_abc import CamelAlias, Resource, register_resource


class CollectionType(StrEnum):
    SINGLE = "Single"
    ARRAY = "Array"


class LifeTime(StrEnum):
    PERPETUAL = "Perpetual"
    TIMEVARIANT = "TimeVariant"


class FieldType(StrEnum):
    STRING = "String"
    BOOLEAN = "Boolean"
    DATE_TIME = "DateTime"
    DECIMAL = "Decimal"


class FieldDefinition(CamelAlias, BaseModel):
    name: str
    lifetime: LifeTime
    type: FieldType
    collection_type: CollectionType = CollectionType.SINGLE
    required: bool
    description: str = ""


# These are optional in the API create and will be given default values. When read is called
# they will not be returned if they have the default value


DEFAULT_FIELD = {"collectionType": "Single", "description": ""}


@register_resource()
class EntityTypeResource(CamelAlias, BaseModel, Resource):
    id: str = Field(exclude=True)
    entity_type_name: str
    display_name: str
    description: str
    field_schema: List[FieldDefinition]

    def read(self, client, old_state) -> Dict[str, Any]:
        entity_type = old_state.entitytype
        return client.request("get", f"/api/api/customentities/entitytypes/{entity_type}").json()

    def create(self, client: httpx.Client):
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        res = client.request("POST", "/api/api/customentities/entitytypes", json=desired).json()
        return {"entitytype": res["entityType"]}

    def update(self, client: httpx.Client, old_state):
        remote = self.read(client, old_state)
        # enrich remote fields with the default values if not present
        remote["fieldSchema"] = [rem | DEFAULT_FIELD for rem in remote["fieldSchema"]]
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        effective = remote | copy.deepcopy(desired)
        for i in range(0, len(self.field_schema)):
            if i < len(remote["fieldSchema"]):
                eff_field = remote["fieldSchema"][i] | desired["fieldSchema"][i]
                effective["fieldSchema"][i] = eff_field
        if effective == remote:
            return None
        res = client.request(
            "PUT", f"/api/api/customentities/entitytypes/{old_state.entitytype}", json=desired
        ).json()
        return {"entitytype": res["entityType"]}

    @staticmethod
    def delete(client, old_state):
        raise RuntimeError("Cannot delete a custom entity definition")

    def deps(self):
        return []
