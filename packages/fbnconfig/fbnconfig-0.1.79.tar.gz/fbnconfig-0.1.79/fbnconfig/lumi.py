from __future__ import annotations

import hashlib
import json
import sys
import textwrap
import time
from enum import StrEnum
from typing import Any, Dict, List

import httpx
from pydantic import BaseModel, Field

from .backoff_handler import BackoffHandler
from .resource_abc import CamelAlias, Ref, Resource, register_resource


# from the sdk
class TaskStatus(StrEnum):
    CREATED = "Created"
    WAITING_FOR_ACTIVATION = "WaitingForActivation"
    WAITING_TO_RUN = "WaitingToRun"
    RUNNING = "Running"
    WAITING_FOR_CHILDREN_TO_COMPLETE = "WaitingForChildrenToComplete"
    RAN_TO_COMPLETION = "RanToCompletion"
    CANCELED = "Canceled"
    FAULTED = "Faulted"


def start_query(client: httpx.Client, sql: str) -> str:
    return client.put(
        "/honeycomb/api/SqlBackground", content=sql, headers={"Content-type": "text/plain"}
    ).json()["executionId"]


def wait_for_background(client, execution_id) -> bool:
    status = get_status(client, execution_id)
    match status:
        case TaskStatus.FAULTED | TaskStatus.CANCELED:
            raise RuntimeError("Query was " + status + ". Execution id: " + execution_id)
        case (
            TaskStatus.CREATED
            | TaskStatus.WAITING_FOR_ACTIVATION
            | TaskStatus.WAITING_TO_RUN
            | TaskStatus.WAITING_FOR_CHILDREN_TO_COMPLETE
        ):
            return False
        case TaskStatus.RUNNING:
            return False
        case TaskStatus.RAN_TO_COMPLETION:
            return True
        case _:
            raise RuntimeError("Unknown status: " + status + ". Execution id: " + execution_id)


def fetch(client, execution_id):
    res = client.get(f"/honeycomb/api/SqlBackground/{execution_id}/jsonproper")
    return res.json()


def get_status(client: httpx.Client, execution_id: str) -> str:
    """Get the status of the query in Luminesce

    Returns:
        str: string containing the query status value.
    """
    return client.get(f"/honeycomb/api/SqlBackground/{execution_id}").json()["status"]


def query(client: httpx.Client, sql: str, backoff_handler: BackoffHandler) -> Dict[Any, Any]:
    execution_id: str = start_query(client, sql)
    progress = False
    while True:
        if progress is False:
            backoff_handler.sleep()
            progress = wait_for_background(client, execution_id)
        else:
            #  Pause after the last wait_for_background_call, otherwise increased chances of 429s
            backoff_handler.sleep()
            return fetch(client, execution_id)


class ParameterType(StrEnum):
    BigInt = "BigInt"
    Boolean = "Boolean"
    Date = "Date"
    DateTime = "DateTime"
    Decimal = "Decimal"
    Double = "Double"
    Int = "Int"
    Table = "Table"
    Text = "Text"


class VariableType(StrEnum):
    Scalar = "@@"
    Table = "@"


class Variable(BaseModel):
    name: str
    type: VariableType
    sql: str

    def init_str(self):
        #  eg @scalar = select 2 + 2
        return f"{self.type.value}{self.name} = {self.sql}"

    def with_str(self):
        return f"{self.type.value}{self.name}"


class Parameter(BaseModel, CamelAlias):
    name: str
    type: ParameterType
    value: Any
    set_as_default_value: bool = True
    is_mandatory: bool = True
    tooltip: str | None = None

    # return in the same format that sys.file stores it in
    def metadata(self):
        base: Dict[str, Any] = {"Name": self.name, "Type": self.type.value, "Description": self.tooltip}
        if self.set_as_default_value and self.type != ParameterType.Table:
            base["DefaultValue"] = self.value
        if self.type == ParameterType.Table:
            if self.is_mandatory:
                base["ConditionUsage"] = 2
            else:
                base["ConditionUsage"] = 0
        return base


def lumi_fmt(value):
    if isinstance(value, Variable):
        return f"{value.type.value}{value.name}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return '"' + value.replace('"', '""') + '"'


@register_resource()
class ViewRef(BaseModel, Ref):
    """Reference an existing view


    Example
    ----------
    >>> from fbnconfig import lumi
    >>> lumi.ViewRef(
    ...  id="lumi-example-ref",
    ...  provider="Views.fbnconfig.existing_view")


    Attributes
    ----------
    id : str
         Resource identifier.
    provider : str
        Name of the view referenced. This is assumed to exist
    """

    id: str = Field(exclude=True)
    provider: str
    _backoff_handler = BackoffHandler()
    _version: str | None = None

    def attach(self, client) -> None:
        res = query(
            client,
            textwrap.dedent(f"""\
                select r.Version from sys.registration as r
                where name = '{self.provider}'
                order by r.Version asc
                limit 1
            """),
            backoff_handler=self._backoff_handler,
        )
        if len(res) != 1:
            raise RuntimeError(f"Failed to attach ref to {self.provider}, the view might not exist")
        self._version = res[0]


@register_resource()
class ViewResource(BaseModel, Resource):
    """Create and manage a Luminesce view

    Example
    ----------
    >>> from fbnconfig import lumi
    >>> lumi.ViewResource(
    ...  id="lumi-example-view",
    ...  provider="Views.fbnconfig.example",
    ...  description="My resource test view",
    ...  documentation_link="http://example.com/query",
    ...  variable_shape=False,
    ...  use_dry_run=True,
    ...  allow_execute_indirectly=False,
    ...  distinct=True,
    ...  sql='select 2+#PARAMETERVALUE(p1)   as   twelve',
    ...  parameters=[
    ...      lumi.Parameter(
    ...          name="p1",
    ...          value=10,
    ...          set_as_default_value=True,
    ...          tooltip="a number",
    ...          type=lumi.ParameterType.INT
    ...      )

    Attributes
    ----------
    id : str
         Resource identifier.
    provider : str
        Name of the view managed by this resource
    description : str
        View description
    sql: str
        The query string for the view
    parameters : list of `Parameter`, optional
        List of parameters for the view
    dependencies : list of dependencies, optional
        This can be another view or any other resource
    documentation_link: str, optional
        Displays one or more hyperlinks in the summary dialog for the view
    variable_shape: bool, optional
        This is useful if data returned is likely to vary in shape between queries. Defaults to false.
    allow_execute_indirectly : bool, optional
        Allows end users to query providers within the view even if they are not entitled to use those
        providers directly.
        Defaults to false.
    limit: int, optional
        Test option when developing view, does not have an effect on a published view. Defaults to None
    group_by: str, optional
        Test option when developing view, does not have an effect on a published view. Defaults to None
    filter: str, optional
        Test option when developing view, does not have an effect on a published view. Defaults to None
    offset: int, optional
        Test option when developing view, does not have an effect on a published view. Defaults to None
    distinct: bool, optional
        Test option when developing view, does not have an effect on a published view. Defaults to None
    use_dry_run: bool, optional
        Intended for automatic deployment of views. See docs for more details. Defaults to false
    variables: List of `Variable`, optional
        A table variable that can be passed into the view by an end user or in code

    See Also
    --------
    `https://support.lusid.com/knowledgebase/article/KA-01767/en-us`__
    """

    id: str = Field(exclude=True)
    provider: str = Field(serialization_alias="Provider")
    description: str = Field(serialization_alias="Description")
    sql: str
    parameters: List[Parameter] = []
    dependencies: List | None = None
    documentation_link: str | None = None
    variable_shape: bool | None = None
    allow_execute_indirectly: bool | None = None
    limit: int | None = None
    group_by: str | None = None
    filter: str | None = None
    offset: int | None = None
    distinct: bool | None = None
    use_dry_run: bool | None = None
    variables: List[Variable] = []

    _backoff_handler = BackoffHandler()

    class Registration:
        tries = 10
        wait_time = 1

    _saved_options = {  # maps from sys.file metadata to view option names
        "Description": "Description",
        "DocumentationLink": "documentationLink",
        "IsWithinDirectProviderView": "variableShape",
        "IsWithinViewAllowingIndirectExecute": "allowExecuteIndirectly",
    }
    _test_options = ["distinct", "filter", "groupby", "limit", "offset", "preamble", "useDryRun"]

    def read(self, client, old_state) -> Dict[str, Any]:
        path = old_state.provider.replace(".", "/")
        res = query(
            client,
            textwrap.dedent(f"""\
                select f.Content, r.Version from sys.file as f
                join sys.registration as r on r.Name = '{old_state.provider}'
                where path = 'databaseproviders/{path}.sql'
                order by r.Version asc
                limit 1
            """),
            self._backoff_handler,
        )
        assert len(res) == 1

        def strip_column_description(kv: Dict) -> Dict:
            if kv["Type"] == "Table":
                kv["Description"] = kv["Description"].split("\nAvailable columns")[0]

            return kv

        parts = res[0]["Content"].split("--- MetaData ---")
        sql = parts[0]
        metadata = json.loads(parts[1])

        parameters = [strip_column_description(p) for p in metadata["Parameters"]]
        props = {
            v: metadata[k] for k, v in self._saved_options.items() if metadata.get(k, None) is not None
        }
        return {"sql": sql, "version": res[0]["Version"], "parameters": parameters} | props

    @staticmethod
    def registration_version(client, view_name, backoff_handler: BackoffHandler) -> int | None:
        content = textwrap.dedent(f"""\
            select Version from sys.registration where Name='{view_name}'
            order by Version asc
            limit 1
        """)
        rows = query(client, content, backoff_handler)
        return int(rows[0]["Version"]) if len(rows) > 0 else None

    @staticmethod
    def format_option(option, value):
        if isinstance(value, bool) and value:
            return f"--{option}"
        if isinstance(value, (int, float)):
            return f"--{option}={value}"
        # we run self.dump by alias, these two have a serialization alias on the dto
        # which ends up as the option, which should be lower
        if option == "Provider" or option == "Description":
            option = option.lower()
        return f"--{option}={lumi_fmt(value)}"

    def get_variables(self):
        param_variables = [param.value for param in self.parameters if isinstance(param.value, Variable)]
        seen = set()
        return [
            value
            for value in self.variables + param_variables
            if value.name not in seen and not seen.add(value.name)
        ]

    def template(self, desired):
        options = [
            self.format_option(option, desired[option])
            for option in ["Provider"] + self._test_options + list(self._saved_options.values())
            if desired.get(option) is not None
        ]

        tpl = textwrap.dedent("""\
            {preamble}@x = use Sys.Admin.SetupView{with_clause}
            {options}{params}
            ----
            {sql}
            enduse;
            select * from @x;
        """)
        params = [
            f"{p.name},{p.type.value},{lumi_fmt(p.value)},{lumi_fmt(p.is_mandatory)}"
            + (f',"{p.tooltip}"' if p.tooltip is not None else "")
            if p.type == ParameterType.Table
            else f"{p.name},{p.type.value},{lumi_fmt(p.value)},{lumi_fmt(p.set_as_default_value)}"
            + (f',"{p.tooltip}"' if p.tooltip is not None else "")
            for p in self.parameters
        ]
        param_clause = "\n--parameters\n{0}".format("\n".join(params)) if len(params) > 0 else ""
        variables = self.get_variables()
        preamble = ";\n".join([v.init_str() for v in variables]) + ";\n" if len(variables) > 0 else ""
        with_clause = (
            " with " + ", ".join([v.with_str() for v in variables]) if len(variables) > 0 else ""
        )
        sql = tpl.format(
            options="\n".join(options),
            params=param_clause,
            sql=desired["sql"],
            with_clause=with_clause,
            preamble=preamble,
        )
        return sql

    def _get_content_hash(self) -> str:
        desired = self.model_dump(exclude_none=True, by_alias=True)
        sql = self.template(desired)
        return hashlib.sha256(sql.encode()).hexdigest()

    def create(self, client) -> Dict[str, Any]:
        desired = self.model_dump(exclude_none=True, by_alias=True)
        sql = self.template(desired)
        query(client, sql, self._backoff_handler)
        for i in range(1, self.Registration.tries + 1):
            if self.registration_version(client, self.provider, self._backoff_handler) is not None:
                break
            else:
                if i == self.Registration.tries:
                    sys.stderr.write(
                        f"warning: no view registration after {i} tries for {self.provider}"
                    )
                else:
                    time.sleep(self.Registration.wait_time)
        return {"provider": self.provider}

    def update(self, client, old_state):
        if self.provider != old_state.provider:
            self.delete(client, old_state)
            self.create(client)
            return {"provider": self.provider}
        desired = self.model_dump(exclude_none=True, by_alias=True, exclude=set(self._test_options))
        raw_remote = self.read(client, old_state)
        remote_props = {
            k.lower(): v
            for k, v in raw_remote.items()
            if k in self._saved_options.values() and v is not None
        }
        desired_props = {
            k.lower(): v
            for k, v in desired.items()
            if k in self._saved_options.values() and v is not None
        }
        remote_params = raw_remote["parameters"]
        desired_params = [p.metadata() for p in self.parameters]
        effective_params = [
            (remote_params[i] | desired_params[i])
            if i < len(remote_params) and remote_params[i]["Name"] == desired_params[i]["Name"]
            else desired_params[i]
            for i, des in enumerate(desired_params)
        ]
        remote_sql = textwrap.dedent(raw_remote["sql"].rstrip())
        remote_version = raw_remote["version"]
        desired_sql = textwrap.dedent(self.sql.rstrip())
        if (
            desired_sql == remote_sql
            and remote_props | desired_props == remote_props
            and effective_params == remote_params
        ):
            return None
        sql = self.template(desired)
        query(client, sql, self._backoff_handler)
        for i in range(1, self.Registration.tries + 1):
            version: int | None = self.registration_version(client, self.provider, self._backoff_handler)
            if version is not None and remote_version < version:
                break
            else:
                if i == self.Registration.tries:
                    sys.stderr.write(
                        f"warning: no view registration after {i} tries for {self.provider}"
                    )
                else:
                    time.sleep(self.Registration.wait_time)
        return {"provider": self.provider}

    def deps(self):
        return self.dependencies if self.dependencies else []

    @staticmethod
    def delete(client, old_state):
        sql = textwrap.dedent(f"""\
        @x = use Sys.Admin.SetupView
        --provider={old_state.provider}
        --deleteProvider
        ----
        select 1 as deleting
        enduse;
        select * from @x;
        """)
        backoff = BackoffHandler()
        query(client, textwrap.dedent(sql), backoff_handler=backoff)
        for i in range(1, ViewResource.Registration.tries + 1):
            if (
                ViewResource.registration_version(
                    client=client, view_name=old_state.provider, backoff_handler=backoff
                )
                is None
            ):
                break
            else:
                if i == ViewResource.Registration.tries:
                    sys.stderr.write(
                        f"warning: no view deregistration after {i} tries for {old_state.provider}"
                    )
                else:
                    time.sleep(ViewResource.Registration.wait_time)
