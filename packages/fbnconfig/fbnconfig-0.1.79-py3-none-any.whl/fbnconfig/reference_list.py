import json
from hashlib import sha256
from typing import Any, Dict, List, Sequence

from pydantic import BaseModel, Field, computed_field, model_validator

from . import property
from .resource_abc import CamelAlias, Ref, Resource, register_resource


class ResourceId(BaseModel):
    scope: str
    code: str


class AddressKeyList(CamelAlias, BaseModel):
    values: list[str]
    reference_list_type: str = Field("AddressKeyList", init=False)


class DecimalList(CamelAlias, BaseModel):
    values: list[float]
    reference_list_type: str = Field("DecimalList", init=False)


class FundIdList(CamelAlias, BaseModel):
    values: list[ResourceId]
    reference_list_type: str = Field("FundIdList", init=False)


class PortfolioGroupIdList(CamelAlias, BaseModel):
    values: list[ResourceId]
    reference_list_type: str = Field("PortfolioGroupIdList", init=False)


class PortfolioIdList(CamelAlias, BaseModel):
    values: list[ResourceId]
    reference_list_type: str = Field("PortfolioIdList", init=False)


class InstrumentList(CamelAlias, BaseModel):
    values: list[str]
    reference_list_type: str = Field("InstrumentList", init=False)


class StringList(CamelAlias, BaseModel):
    values: list[str]
    reference_list_type: str = Field("StringList", init=False)


class MetricValue(BaseModel):
    value: float
    unit: str | None


class PropertyListItem(CamelAlias, BaseModel):
    property_definition: property.DefinitionResource | property.DefinitionRef = Field(exclude=True)
    label_value: str | None
    metric_value: MetricValue | None
    label_set_value: Sequence[str] | None
    effective_from: str | None = None
    effective_until: str | None = None

    @computed_field(alias="key")
    def key(self) -> str:
        pd = self.property_definition
        return "/".join([pd.domain.value, pd.scope, pd.code])

    @model_validator(mode="after")
    def validate_one_value_exists(self):
        fields = ["label_value", "metric_value", "label_set_value"]
        s = [field for field in fields if getattr(self, field) is not None]
        if len(s) > 1:
            raise KeyError(f"Cannot set {' and '.join(s)}, only one of {' or '.join(fields)} can be set")
        return self


class PropertyList(CamelAlias, BaseModel):
    values: list[PropertyListItem]
    reference_list_type: str = Field("PropertyList", init=False, exclude=True)


ReferenceListTypes = AddressKeyList | DecimalList | FundIdList | PortfolioGroupIdList | \
    PortfolioIdList | InstrumentList | StringList | PropertyList | PropertyListItem


@register_resource()
class ReferenceListResource(BaseModel, Resource):
    id: str = Field(exclude=True)
    scope: str = Field(exclude=True, init=True)
    code: str = Field(exclude=True, init=True)
    name: str
    description: str | None = None
    tags: list[str] | None = None
    reference_list: ReferenceListTypes

    @computed_field(alias="id")
    def list_id(self) -> dict[str, str]:
        return {"scope": self.scope, "code": self.code}

    def read(self, client, old_state):
        scope, code = old_state.scope, old_state.code
        url = f"/api/api/referencelists/{scope}/{code}"
        entity = client.get(url).json()
        entity.pop("version", None)
        return entity

    def create(self, client) -> Dict[str, Any]:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        sorted_desired = json.dumps(desired, sort_keys=True)
        content_hash = sha256(sorted_desired.encode()).hexdigest()
        client.request("POST", "/api/api/referencelists", json=desired)
        return {"scope": self.scope, "code": self.code, "content_hash": content_hash}

    def update(self, client, old_state):
        if (self.scope, self.code) != (old_state.scope, old_state.code):
            self.delete(client, old_state)
            return self.create(client)
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        sorted_desired = json.dumps(desired, sort_keys=True)
        desired_hash = sha256(sorted_desired.encode()).hexdigest()
        if desired_hash == old_state.content_hash:
            return None
        client.request("POST", "/api/api/referencelists", json=desired)
        return {"scope": self.scope, "code": self.code, "content_hash": desired_hash}

    @staticmethod
    def delete(client, old_state):
        client.request("DELETE", f"/api/api/referencelists/{old_state.scope}/{old_state.code}")

    def deps(self) -> List[Resource | Ref]:
        if isinstance(self.reference_list, PropertyList):
            props = {i.property_definition.id: i.property_definition for i in self.reference_list.values}
            return list(props.values())
        return []
