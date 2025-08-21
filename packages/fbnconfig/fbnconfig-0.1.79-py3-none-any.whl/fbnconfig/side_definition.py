from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence

import httpx
from pydantic import BaseModel, Field, field_serializer

from .property import DefinitionRef, DefinitionResource
from .resource_abc import Ref, Resource, register_resource


@register_resource()
class SideRef(BaseModel, Ref):
    """Used to reference an existing side
    Example
    -------
    >>> from fbnconfig.side_definition import SideRef
    >>> side = SideRef(id="side", scope="scope", side="side")
    """

    id: str = Field(exclude=True)
    scope: str = Field(exclude=True)
    side: str

    def attach(self, client):
        scope, side = self.scope, self.side
        try:
            client.get(f"/api/api/transactionconfiguration/sides/{side}", params={"scope": scope})
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Side {self.side} does not exist in scope {self.scope}")
            else:
                raise ex


@register_resource()
class SideResource(BaseModel, Resource):
    """Create a side definition

    Example
    -------
    >>> from fbnconfig.side_definition import SideResource
    >>> side = SideResource(
    >>>     id="side",
    >>>     side="side",
    >>>     scope="scope",
    >>>     security="Txn:LusidInstrumentId",
    >>>     currency = "Txn:TradeCurrency",
    >>>     rate = "Txn:TradeToPortfolioRate",
    >>>     units = "Txn:Units",
    >>>     amount = "Txn:TotalConsideration",
    >>>     notional_amount = "0"
    >>> )
    """

    id: str = Field(exclude=True, init=True)
    side: str
    scope: str = Field(exclude=True)
    security: str | DefinitionRef | DefinitionResource
    currency: str | DefinitionRef | DefinitionResource
    rate: str | DefinitionRef | DefinitionResource
    units: str | DefinitionRef | DefinitionResource
    amount: str | DefinitionRef | DefinitionResource
    notional_amount: str | DefinitionRef | DefinitionResource

    @field_serializer(
        "security", "currency", "rate", "units", "amount", "notional_amount", when_used="always"
    )
    def serialize_fields(self, value) -> str:
        if isinstance(value, (DefinitionRef, DefinitionResource)):
            return f"{value.domain.value}/{value.scope}/{value.code}"
        else:
            return value

    def create(self, client: httpx.Client) -> Optional[Dict[str, Any]]:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        scope = self.scope
        client.put(
            f"/api/api/transactionconfiguration/sides/{self.side}", json=desired, params={"scope": scope}
        )
        return {"side": self.side, "scope": self.scope}

    def read(self, client: httpx.Client, old_state: SimpleNamespace):
        side = old_state.side
        scope = old_state.scope
        return client.get(
            f"/api/api/transactionconfiguration/sides/{side}", params={"scope": scope}
        ).json()

    def update(self, client: httpx.Client, old_state: SimpleNamespace):
        # Check for scope or name change, must delete and create
        if [old_state.side, old_state.scope] != [self.side, self.scope]:
            self.delete(client, old_state)
            return self.create(client)

        # Has there been a change?
        remote = self.read(client, old_state) or {}
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        effective = remote | desired
        if effective == remote:
            return None

        return self.create(client)

    @staticmethod
    def delete(client: httpx.Client, old_state: SimpleNamespace):
        side, scope = old_state.side, old_state.scope
        client.delete(f"/api/api/transactionconfiguration/sides/{side}/$delete", params={"scope": scope})

    def deps(self) -> Sequence[Resource | Ref]:
        return [
            value
            for value in (
                self.security,
                self.currency,
                self.amount,
                self.rate,
                self.units,
                self.notional_amount,
            )
            if isinstance(value, (DefinitionResource, DefinitionRef))
        ]
