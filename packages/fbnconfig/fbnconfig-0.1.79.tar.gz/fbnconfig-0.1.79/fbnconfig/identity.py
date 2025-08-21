from __future__ import annotations

import copy
import json
from enum import StrEnum
from hashlib import sha256
from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Union

import httpx
from pydantic import BaseModel, Field

from .resource_abc import Ref, Resource, register_resource


@register_resource()
class IdentityRoleRef(BaseModel, Ref):
    """Used to reference an existing identity role for role assignment
    Example
    -------
    >>> from fbnconfig.identity import IdentityRoleRef
    >>> admin = IdentityRoleRef(id="admin", name="lusid-administrator")
    """

    role_id: str | None = Field(None, exclude=True, init=False)
    name: str
    id: str = Field(exclude=True)

    def attach(self, client):
        search = client.request("get", "/identity/api/roles")
        try:
            match = next(role for role in search.json() if role["name"] == self.name)
        except StopIteration:
            raise (RuntimeError("No matching identity role with name", self.name))
        self.role_id = match["id"]


@register_resource()
class IdentityRoleResource(BaseModel, Resource):
    """Manage a role

    Example
    -------
    >>> from fbnconfig.identity import IdentityRoleResource
    >>> operator =
    >>> IdentityRoleResource(id="export-role", description="scheduler-operators", name="export-admin")
    """

    id: str = Field(exclude=True)
    name: str
    description: str
    scope: str | None = Field(None, exclude=True, init=False)
    code: str | None = Field(None, exclude=True, init=False)
    role_id: str | None = Field(None, exclude=True, init=False)
    remote: Dict[str, Any] = Field(None, exclude=True, init=False)

    def read(self, client, old_state):
        get = client.request("get", f"/identity/api/roles/{old_state.roleId}")
        remote = get.json()
        remote.pop("id")
        remote.pop("name")
        remote.pop("roleId")
        remote.pop("source")
        remote.pop("samlName")
        self.remote = remote
        self.role_id = old_state.roleId

    def create(self, client: httpx.Client):
        desired = self.model_dump(mode="json", exclude_none=True)
        res = client.request("POST", "/identity/api/roles", json=desired)
        result = res.json()
        self.scope = result["roleId"]["scope"]
        self.code = result["roleId"]["code"]
        self.role_id = res.json()["id"]
        return {
            "id": self.id,
            "code": self.code,
            "scope": self.scope,
            "name": self.name,
            "roleId": self.role_id,
        }

    def update(self, client: httpx.Client, old_state):
        if self.name != old_state.name:
            raise (RuntimeError("Cannot change the name on a role"))
        self.read(client, old_state)
        remote = copy.deepcopy(self.remote)
        self.role_id = old_state.roleId
        desired = self.model_dump(mode="json", exclude_none=True, exclude={"name"})

        if desired == remote:
            return None
        client.request("put", f"/identity/api/roles/{old_state.roleId}", json=desired)

    @staticmethod
    def delete(client, old_state):
        client.request("DELETE", f"/identity/api/roles/{old_state.roleId}")

    def deps(self):
        return []


class UserType(StrEnum):
    """User type used with a UserResource"""

    PERSONAL = "Personal"
    SERVICE = "Service"


@register_resource()
class UserRef(BaseModel, Ref):
    """Reference an existing user

    Example
    -------
    >>> from fbnconfig.identity import UserRef
    >>> user =  UserRef(id="export-user", login="exports@company.com")
    """

    id: str = Field(exclude=True)
    login: str
    user_id: str | None = Field(None, exclude=True, init=False)

    def attach(self, client):
        user_list = client.request("get", "/identity/api/users")
        match = next((user for user in user_list.json() if user["login"] == self.login), None)
        if match is None:
            raise RuntimeError(f"No user with login {self.login} exists in the remote")
        self.user_id = match["id"]


@register_resource()
class UserResource(BaseModel, Resource):
    """Define a user"""

    id: str = Field(exclude=True)
    first_name: str
    last_name: str
    email_address: str
    second_email_address: Optional[str] = None
    login: str
    type: UserType
    user_id: str | None = Field(None, exclude=True, init=False)
    remote: Dict[str, Any] = Field({}, exclude=True, init=False)

    def read(self, client, old_state):
        get = client.request("get", f"/identity/api/users/{old_state.userId}")
        remote = get.json()
        remote.pop("status", None)
        remote.pop("external", None)
        remote.pop("id", None)
        remote.pop("roles", None)
        remote.pop("links", None)
        self.remote = remote
        self.user_id = old_state.userId

    def create(self, client: httpx.Client) -> Dict[str, Any]:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        res = client.request("POST", "/identity/api/users", json=desired)
        result = res.json()
        self.user_id = result["id"]
        return {"id": self.id, "userId": self.user_id}

    def update(self, client: httpx.Client, old_state):
        self.read(client, old_state)
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        if desired == self.remote:
            return None
        if self.login != self.remote["login"]:
            raise RuntimeError("Cannot change the login on an existing user")
        client.request("put", f"/identity/api/users/{old_state.userId}", json=desired)
        return {"id": self.id, "userId": self.user_id}

    @staticmethod
    def delete(client, old_state):
        client.request("delete", f"/identity/api/users/{old_state.userId}")

    def deps(self):
        return []


@register_resource()
class RoleAssignment(BaseModel, Resource):
    """Assign a role to a user"""

    id: str = Field(exclude=True)
    user: UserResource | UserRef
    role: IdentityRoleResource | IdentityRoleRef
    role_id: str | None = Field(None, exclude=True, init=False)
    user_id: str | None = Field(None, exclude=True, init=False)
    remote: Dict[str, Any] = Field(None, exclude=True, init=False)

    def read(self, client, old_state):
        self.role_id = old_state.roleId
        self.user_id = old_state.userId

    def create(self, client: httpx.Client) -> Dict[str, Any]:
        role_id = self.role.role_id
        user_id = self.user.user_id
        client.request("put", f"/identity/api/roles/{role_id}/users/{user_id}")
        return {"id": self.id, "userId": user_id, "roleId": role_id}

    @staticmethod
    def delete(client: httpx.Client, old_state) -> None:
        role_id = old_state.roleId
        user_id = old_state.userId
        client.request("delete", f"/identity/api/roles/{role_id}/users/{user_id}")

    def update(self, client, old_state) -> Dict[str, Any] | None:
        if old_state.userId == self.user.user_id and old_state.roleId == self.role.role_id:
            return None
        try:
            client.request("delete", f"/identity/api/roles/{old_state.roleId}/users/{old_state.userId}")
        except httpx.HTTPStatusError as e:
            # ignore 404 because if the old role or user are gone this won't exist
            if e.response.status_code != httpx.codes.NOT_FOUND:
                raise
            pass
        client.request("put", f"/identity/api/roles/{self.role.role_id}/users/{self.user.user_id}")
        return {"id": self.id, "userId": self.user.user_id, "roleId": self.role.role_id}

    def deps(self):
        return [self.user, self.role]


@register_resource()
class ApplicationRef(BaseModel, Ref):
    """Reference an existing application

    Example
    -------
    >>> from fbnconfig.identity import ApplicationRef
    >>> application = ApplicationRef(id="application", client_id="client-id")
    """

    id: str = Field(exclude=True)
    client_id: str = Field(None, serialization_alias="clientId")
    application_id: str | None = Field(None, exclude=True, init=False)

    def attach(self, client):
        search = client.get("/identity/api/applications")
        try:
            match = next(app for app in search.json() if app["clientId"] == self.client_id)
        except StopIteration:
            raise RuntimeError(f"No matching application with client ID {self.client_id}")
        self.application_id = match["id"]


class ApplicationType(StrEnum):
    NATIVE = "Native"
    WEB = "Web"


@register_resource()
class ApplicationResource(BaseModel, Resource):
    """Define an application in LUSID

    Example
    -------
    >>> from fbnconfig.identity import ApplicationResource
    >>> application_secrets =
    >>> ApplicationResource(id="application", client_id="client-id", display_name="Display Name")
    """

    id: str = Field(exclude=True)
    client_id: str = Field(None, serialization_alias="clientId")
    display_name: str = Field(None, serialization_alias="displayName")
    application_type: ApplicationType = Field(None, serialization_alias="type")
    application_id: str | None = Field(None, exclude=True, init=False, serialization_alias="id")
    secret: str | None = Field(None, exclude=True, init=False)
    issuer: str | None = Field(None, exclude=True, init=False)
    redirect_uris: list[str] | None = Field(
        None, exclude=True, init=False, serialization_alias="redirectUris"
    )
    post_logout_redirect_uris: list[str] | None = Field(
        None, exclude=True, init=False, serialization_alias="postLogoutRedirectUris"
    )

    def __get_content_hash__(self) -> str:
        dump = self.model_dump(mode="json", exclude_none=True, by_alias=True, exclude={"secret"})
        return sha256(json.dumps(dump, sort_keys=True).encode()).hexdigest()

    def __setattr__(self, name: str, value: Any) -> None:
        # Make application_id, secret, and issuer readonly after initialization
        if hasattr(self, "_initialized") and name in ("application_id", "secret", "issuer"):
            raise AttributeError(f"Field '{name}' is readonly and cannot be modified")
        super().__setattr__(name, value)

    def model_post_init(self, __context: Any) -> None:
        # Mark as initialized to enable readonly protection
        object.__setattr__(self, "_initialized", True)

    def get_token_url(self) -> str:
        """Appends /v1/token to the issuer URL to get the token endpoint."""
        if self.issuer is None:
            raise RuntimeError("Application must be created before getting the token URL")
        return f"{self.issuer}/v1/token"

    def read(self, client: httpx.Client, old_state: SimpleNamespace) -> None | Dict[str, Any]:
        return client.get(f"/identity/api/applications/{old_state.application_id}").json()

    def create(self, client: httpx.Client) -> Optional[Dict[str, Any]]:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        response = client.post("/identity/api/applications", json=desired).json()

        # Store secret before popping it
        secret = response.get("secret")
        response.pop("secret", None)

        # Temporarily disable readonly protection to set values
        object.__setattr__(self, "application_id", response["id"])
        object.__setattr__(self, "secret", secret)
        object.__setattr__(self, "issuer", response.get("issuer"))

        return {
            "id": self.id,
            "application_id": response["id"],
            "client_id": response.get("clientId", self.client_id),
            "source_version": self.__get_content_hash__(),
            "remote_version": sha256(json.dumps(response, sort_keys=True).encode()).hexdigest(),
        }

    def update(self, client: httpx.Client, old_state) -> Union[None, Dict[str, Any]]:
        source_hash = self.__get_content_hash__()
        remote = self.read(client, old_state)
        remote_hash = sha256(json.dumps(remote, sort_keys=True).encode()).hexdigest()

        if remote_hash == old_state.remote_version and source_hash == old_state.source_version:
            return None

        self.delete(client, old_state)
        return self.create(client)

    @staticmethod
    def delete(client: httpx.Client, old_state) -> None:
        client.delete(f"/identity/api/applications/{old_state.application_id}")

    def deps(self) -> Sequence["Resource|Ref"]:
        return []
