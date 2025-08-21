from __future__ import annotations

from enum import StrEnum
from types import SimpleNamespace
from typing import Any, Dict, List

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from .datatype import DataTypeRef, DataTypeResource
from .resource_abc import CamelAlias, Ref, Resource, register_resource


class LifeTime(StrEnum):
    Perpetual = "Perpetual"
    TimeVariant = "TimeVariant"


class Domain(StrEnum):
    Abor = "Abor"
    AborConfiguration = "AborConfiguration"
    AccessMetadata = "AccessMetadata"
    Account = "Account"
    Allocation = "Allocation"
    Analytic = "Analytic"
    Block = "Block"
    Calendar = "Calendar"
    ChartOfAccounts = "ChartOfAccounts"
    Compliance = "Compliance"
    ConfigurationRecipe = "ConfigurationRecipe"
    CustodianAccount = "CustodianAccount"
    CustomEntity = "CustomEntity"
    CutLabelDefinition = "CutLabelDefinition"
    DerivedValuation = "DerivedValuation"
    DiaryEntry = "DiaryEntry"
    Execution = "Execution"
    Fund = "Fund"
    Holding = "Holding"
    Instrument = "Instrument"
    InstrumentEvent = "InstrumentEvent"
    Leg = "Leg"
    LegalEntity = "LegalEntity"
    MarketData = "MarketData"
    NextBestAction = "NextBestAction"
    NotDefined = "NotDefined"
    Order = "Order"
    OrderInstruction = "OrderInstruction"
    Package = "Package"
    Participation = "Participation"
    Person = "Person"
    Placement = "Placement"
    Portfolio = "Portfolio"
    PortfolioGroup = "PortfolioGroup"
    PropertyDefinition = "PropertyDefinition"
    Reconciliation = "Reconciliation"
    ReferenceHolding = "ReferenceHolding"
    Transaction = "Transaction"
    TransactionConfiguration = "TransactionConfiguration"
    UnitResult = "UnitResult"


class ResourceId(BaseModel):
    scope: str
    code: str


class ConstraintStyle(StrEnum):
    Property = "Property"
    Collection = "Collection"
    Identifier = "Identifier"


class CollectionType(StrEnum):
    Set = "Set"
    Array = "Array"


@register_resource()
class DefinitionRef(BaseModel, Ref):
    id: str = Field(exclude=True)
    domain: Domain
    scope: str
    code: str

    def __format__(self, _):
        return f"Properties[{self.domain}/{self.scope}/{self.code}]"

    def attach(self, client):
        domain, scope, code = self.domain, self.scope, self.code
        try:
            client.get(f"/api/api/propertydefinitions/{domain}/{scope}/{code}")
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Property definition {domain}/{scope}/{code} not found")
            else:
                raise ex


class Formula:
    formula: str
    args: Dict

    def __init__(self, formula, **kwargs):
        self.formula = formula
        self.args = kwargs


@register_resource()
class DefinitionResource(CamelAlias, BaseModel, Resource):
    id: str = Field(init=True, exclude=True)
    domain: Domain
    scope: str
    code: str
    display_name: str
    data_type_id: ResourceId | DataTypeRef | DataTypeResource
    property_description: str | None = None
    life_time: LifeTime | None = None
    constraint_style: ConstraintStyle | None = None
    collection_type: str | None = None
    derivation_formula: Formula | None = None
    is_filterable: bool | None = None
    remote: Dict[str, Any] | None = Field(None, exclude=True, init=False)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __format__(self, _):
        return f"Properties[{self.domain}/{self.scope}/{self.code}]"

    @field_serializer("derivation_formula", when_used="always")
    def formula_ser(self, value: Formula) -> str:
        # uses str.format to interpolate the values
        return value.formula.format(**value.args)

    @field_serializer("data_type_id", when_used="always")
    def datatype_ser(self, value: ResourceId | DataTypeRef | DataTypeResource) -> Dict[str, str]:
        # uses str.format to interpolate the values
        return {"scope": value.scope, "code": value.code}

    @model_validator(mode="after")
    def check_derived_or_plain(self):
        if self.derivation_formula:
            if self.life_time or self.constraint_style or self.collection_type:
                raise RuntimeError("A property must be either derived or plain")
        # if this is not a derived property, then is_filterable cannot be set
        elif self.is_filterable is not None:
            raise RuntimeError(
                "Cannot set 'is_filterable' field, a property must be either derived or plain"
            )
        return self

    def read(self, client, old_state):
        domain = old_state.domain
        scope = old_state.scope
        code = old_state.code
        self.remote = client.get(f"/api/api/propertydefinitions/{domain}/{scope}/{code}").json()
        return self.remote

    def create(self, client: httpx.Client):
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        derived = self.derivation_formula is not None
        if derived:
            client.post("/api/api/propertydefinitions/derived", json=desired)
        else:
            client.post("/api/api/propertydefinitions", json=desired)
        return {"domain": self.domain, "scope": self.scope, "code": self.code, "derived": derived}

    @staticmethod
    def delete(client, old_state: SimpleNamespace):
        domain, scope, code = old_state.domain, old_state.scope, old_state.code
        client.delete(f"/api/api/propertydefinitions/{domain}/{scope}/{code}")

    def update(self, client, old_state):
        # cannot change identifier or switch derived and non-derived. recreate
        derived = self.derivation_formula is not None
        if [self.domain, self.scope, self.code, derived] != [
            old_state.domain,
            old_state.scope,
            old_state.code,
            old_state.derived,
        ]:
            self.delete(client, old_state)
            return self.create(client)
        self.read(client, old_state)
        remote = self.remote or {}
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        effective = remote | desired
        if effective == remote:
            return None
        # cannot change dataType, or collectionType need to recreate
        if remote["dataTypeId"] != desired["dataTypeId"] or remote.get(
            "collectionType", None
        ) != effective.get("collectionType", None):
            self.delete(client, old_state)
            return self.create(client)
        if derived:
            client.put(
                f"/api/api/propertydefinitions/derived/{self.domain}/{self.scope}/{self.code}",
                json=desired,
            )
        else:
            client.put(
                f"/api/api/propertydefinitions/{self.domain}/{self.scope}/{self.code}", json=desired
            )
        return {"domain": self.domain, "scope": self.scope, "code": self.code, "derived": derived}

    def deps(self):
        res: List[Resource | Ref] = []
        if self.derivation_formula:
            res = [
                value
                for value in self.derivation_formula.args.values()
                if isinstance(value, (DefinitionResource, DefinitionRef))
            ]
        if isinstance(self.data_type_id, (Resource, Ref)):
            res.append(self.data_type_id)
        return res
