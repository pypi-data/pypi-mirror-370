from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from types import SimpleNamespace
from typing import Any

import httpx
from httpx import Client as httpxClient
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer, model_serializer

from . import identity, lumi, scheduler
from .resource_abc import CamelAlias, Ref, Resource, register_resource


@register_resource()
class WorkerRef(BaseModel, Ref):
    """Reference an existing worker

    Example
    ----------
    >>> from fbnconfig import workflows
    >>> workflows.WorkerRef(
    ...  id="reconciliation-worker",
    ...  scope="default",
    ...  code="GroupReconciliation")


    Attributes
    ----------
    id : str
         Resource identifier.
    scope : str
        Scope of the worker.
    code: str
        Code of the worker.
    """

    id: str = Field(exclude=True)
    scope: str
    code: str

    def attach(self, client):
        try:
            client.get(f"/workflow/api/workers/{self.scope}/{self.code}")
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Worker {self.scope}/{self.code} does not exist")
            else:
                raise ex


@register_resource()
class WorkerResource(BaseModel, Resource):
    """Define a worker

    Example
    ----------
    >>> from fbnconfig import workflows
    >>> workflows.WorkerResource(
    ...  id="myworker",
    ...  scope="default",
    ...  code="MyWorker",
    ...  display_name="DoSomeWork",
    ...  description="New description",
    ...  worker_configuration=workflows.LuminesceView(
    ...    view=lumi.ViewRef(id="my-view", provider="Views.Unit.Something"))
    ... )


    Attributes
    ----------
    id : str
         Resource identifier.
    scope : str
        Scope of the worker.
    code: str
        Code of the worker.
    display_name: str
        Human-readable name for the worker
    description: str | None
        Optional description of the worker
    worker_configuration: Fail | HealthCheck | LuminesceView | SchedulerJob | Sleep
        Worker configuration

    """

    id: str = Field(exclude=True)
    scope: str = Field(exclude=True, init=True)
    code: str = Field(exclude=True, init=True)
    display_name: str
    description: str | None = None
    worker_configuration: Fail | HealthCheck | LuminesceView | SchedulerJob | Sleep

    @computed_field(alias="id")
    def worker_id(self) -> dict[str, str]:
        return {"scope": self.scope, "code": self.code}

    def read(self, client: httpxClient, old_state: SimpleNamespace) -> dict[str, Any] | None:
        scope = old_state.scope
        code = old_state.code
        return client.get(f"/workflow/api/workers/{scope}/{code}").json()

    # noinspection PyProtectedMember
    def __resolve_worker_version(self) -> str:
        if isinstance(self.worker_configuration, SchedulerJob):
            if isinstance(self.worker_configuration.job, scheduler.JobResource):
                dump = self.worker_configuration.job.model_dump(
                    mode="json", exclude_none=True, by_alias=True
                )
                return hashlib.sha256(json.dumps(dump, sort_keys=True).encode()).hexdigest()
            if isinstance(self.worker_configuration.job, scheduler.JobRef):
                # noinspection PyProtectedMember
                version = self.worker_configuration.job._content_hash
                ref_id = f"{self.worker_configuration.job_id}"
                assert version is not None, f"Expected JobRef {ref_id} to be attached"
                return version

        if isinstance(self.worker_configuration, LuminesceView):
            if isinstance(self.worker_configuration.view, lumi.ViewResource):
                return self.worker_configuration.view._get_content_hash()
            if isinstance(self.worker_configuration.view, lumi.ViewRef):
                return self.worker_configuration.view._version or "0"
        return "0"

    def create(self, client: httpxClient) -> dict[str, Any] | None:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        client.post("/workflow/api/workers", json=desired)

        return {
            "id": self.id,
            "scope": self.scope,
            "code": self.code,
            "worker_version": self.__resolve_worker_version(),
        }

    def update(self, client: httpxClient, old_state: SimpleNamespace) -> dict[str, Any] | None:
        if [self.scope, self.code] != [old_state.scope, old_state.code]:
            self.delete(client, old_state)
            return self.create(client)

        remote = self.read(client, old_state) or {}
        remote.pop("version")
        remote.pop("parameters")
        remote.pop("resultFields")
        remote.pop("links")
        remote.pop("id")

        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True, exclude={"worker_id"})
        effective = remote | desired
        if desired == effective and old_state.worker_version == self.__resolve_worker_version():
            return None

        client.put(f"/workflow/api/workers/{self.scope}/{self.code}", json=desired).json()
        return {
            "id": self.id,
            "scope": self.scope,
            "code": self.code,
            "worker_version": self.__resolve_worker_version(),
        }

    @staticmethod
    def delete(client: httpxClient, old_state: SimpleNamespace) -> None:
        client.delete(f"/workflow/api/workers/{old_state.scope}/{old_state.code}")

    def deps(self) -> list[Any]:
        if isinstance(self.worker_configuration, LuminesceView) and isinstance(
            self.worker_configuration.view, (lumi.ViewResource, lumi.ViewRef)
        ):
            return [self.worker_configuration.view]
        if isinstance(self.worker_configuration, SchedulerJob):
            return [self.worker_configuration.job]
        return []


@register_resource()
class TaskDefinitionRef(BaseModel, Ref):
    """Reference an existing task definition

    Example
    ----------
    >>> from fbnconfig import workflows
    >>> workflows.TaskDefinitionRef(
    ...  id="task-definition-ref",
    ...  scope="DQ",
    ...  code="ExceptionTask")


    Attributes
    ----------
    id : str
         Resource identifier.
    scope : str
        Scope of the task definition.
    code: str
        Code of the task definition.
    """

    id: str = Field(exclude=True)
    scope: str
    code: str

    def attach(self, client):
        try:
            client.get(f"/workflow/api/taskdefinitions/{self.scope}/{self.code}").json()
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Task definition {self.scope}/{self.code} does not exist")
            else:
                raise ex


@register_resource()
class TaskDefinitionResource(BaseModel, Resource):
    id: str = Field(exclude=True)
    scope: str = Field(exclude=True)
    code: str = Field(exclude=True)
    display_name: str
    initial_state: InitialState
    states: list[TaskStateDefinition]
    description: str | None = None
    triggers: list[TriggerDefinition] | None = None
    transitions: list[TaskTransitionDefinition] | None = None
    field_schema: list[TaskFieldDefinition] | None = None
    actions: list[ActionDefinition] | None = None

    @computed_field(alias="id")
    def task_def_id(self) -> dict[str, str]:
        return {"scope": self.scope, "code": self.code}

    def read(self, client: httpxClient, old_state: SimpleNamespace) -> None | dict[str, Any]:
        remote = client.get(f"/workflow/api/taskdefinitions/{old_state.scope}/{old_state.code}").json()
        return remote

    def create(self, client: httpxClient) -> dict[str, Any] | None:
        desired = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        source_version = hashlib.sha256(json.dumps(desired, sort_keys=True).encode()).hexdigest()
        remote_version = client.post("/workflow/api/taskdefinitions", json=desired).json()["version"][
            "asAtVersionNumber"
        ]
        return {
            "id": self.id,
            "scope": self.scope,
            "code": self.code,
            "source_version": source_version,
            "remote_version": remote_version,
        }

    def update(self, client: httpxClient, old_state) -> dict[str, Any] | None:
        if self.scope != old_state.scope or self.code != old_state.code:
            self.delete(client, old_state)
            return self.create(client)

        remote = self.read(client, old_state) or {}
        desired = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        remote_version = remote["version"]["asAtVersionNumber"]
        source_version = hashlib.sha256(json.dumps(desired, sort_keys=True).encode()).hexdigest()
        if source_version == old_state.source_version and remote_version == old_state.remote_version:
            return None

        remote_version = client.put(
            f"/workflow/api/taskdefinitions/{self.scope}/{self.code}", json=desired
        ).json()["version"]["asAtVersionNumber"]
        return {
            "id": self.id,
            "scope": self.scope,
            "code": self.code,
            "source_version": source_version,
            "remote_version": remote_version,
        }

    @staticmethod
    def delete(client: httpxClient, old_state) -> None:
        client.delete(f"/workflow/api/taskdefinitions/{old_state.scope}/{old_state.code}")

    def deps(self) -> list[Any]:
        deps = []
        for t in self.transitions if self.transitions else []:
            deps.extend(t.deps())
        for a in self.actions if self.actions else []:
            deps.extend(a.deps())

        return deps


class EventStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class EventMatchingPattern(BaseModel, CamelAlias):
    event_type: str
    filter: str | None = None


class EventHandlerMapping(BaseModel, CamelAlias):
    map_from: str | None = None
    set_to: str | None = None


class CreateNewTaskActivity(BaseModel, CamelAlias):
    type: str = Field(init=False, default="CreateNewTask")
    correlation_ids: list[EventHandlerMapping] | None = None
    task_fields: dict[str | TaskFieldDefinition, FieldMapping] | None = None
    initial_trigger: str | TriggerDefinition | None = None

    @field_serializer("initial_trigger")
    def trigger_serializer(self, initial_trigger: str | TriggerDefinition | None) -> str | None:
        return (
            initial_trigger.name if isinstance(initial_trigger, TriggerDefinition) else initial_trigger
        )

    @field_serializer("task_fields")
    def task_fields_serializer(self, task_fields: dict[str | TaskFieldDefinition, FieldMapping]):
        return {k.name if isinstance(k, TaskFieldDefinition) else k: v for k, v in task_fields.items()}


class UpdateMatchingTasksActivity(BaseModel, CamelAlias):
    type: str = Field(init=False, default="UpdateMatchingTasks")
    correlation_ids: list[EventHandlerMapping] | None = None
    task_fields: dict[str, FieldMapping] | None = None
    filter: str | None = None
    trigger: str | TriggerDefinition

    @field_serializer("trigger")
    def trigger_serializer(self, trigger: str | TriggerDefinition) -> str:
        return trigger.name if isinstance(trigger, TriggerDefinition) else trigger


class Fail(BaseModel):
    type: str = Field(init=False, default="Fail")


class HealthCheck(BaseModel):
    type: str = Field(init=False, default="HealthCheck")
    url: str


class LuminesceView(BaseModel):
    type: str = Field(init=False, default="LuminesceView")
    view: lumi.ViewResource | lumi.ViewRef = Field(exclude=True, init=True)

    @computed_field
    def name(self) -> str:
        return self.view.provider


class SchedulerJob(BaseModel):
    type: str = Field(init=False, default="SchedulerJob")
    job: scheduler.JobRef | scheduler.JobResource = Field(exclude=True, init=True)

    @computed_field(alias="jobId")
    def job_id(self) -> dict[str, str]:
        assert self.job is not None, "Job should not be None"
        return {"scope": self.job.scope, "code": self.job.code}


class Sleep(BaseModel):
    type: str = Field(init=False, default="Sleep")


class TaskStateDefinition(BaseModel):
    model_config = ConfigDict(use_enum_values=True, frozen=True)
    name: str


class TaskFieldDefinitionType(StrEnum):
    STRING = "String"
    DECIMAL = "Decimal"
    DATETIME = "DateTime"
    BOOLEAN = "Boolean"


class ReadOnlyStateType(StrEnum):
    ALL_STATES = "AllStates"
    INITIAL_STATE = "InitialState"
    TERMINAL_STATE = "TerminalState"
    SELECTED_STATES = "SelectedStates"


class ReadOnlyStates(BaseModel, CamelAlias):
    model_config = ConfigDict(use_enum_values=True, frozen=True)
    state_type: str | ReadOnlyStateType
    selected_states: list[str | TaskStateDefinition] | None = None

    @field_serializer("selected_states")
    def states(self, selected_states) -> list[str] | None:
        return [s.name if isinstance(s, TaskStateDefinition) else s for s in selected_states]

    def __hash__(self) -> int:
        return hash((self.state_type, frozenset(self.selected_states or frozenset())))


class ValueConstraintType(StrEnum):
    SUGGESTED = "Suggested"
    VALIDATED = "Validated"


class ValueSourceType(StrEnum):
    ACCEPTABLE_VALUES = "AcceptableValues"


class ValueConstraints(BaseModel, CamelAlias):
    model_config = ConfigDict(use_enum_values=True, frozen=True)
    constraint_type: str | ValueConstraintType
    value_source_type: str | ValueSourceType
    acceptable_values: list[str]

    def __hash__(self) -> int:
        return hash((self.constraint_type, self.value_source_type, frozenset(self.acceptable_values)))


class TaskFieldDefinition(BaseModel, CamelAlias):
    model_config = ConfigDict(use_enum_values=True, frozen=True)
    name: str
    type: str | TaskFieldDefinitionType
    read_only_states: ReadOnlyStates | None = None
    value_constraints: ValueConstraints | None = None

    @field_serializer("type")
    def type_serializer(self, field_type: str | TaskFieldDefinitionType | None):
        return field_type.name if isinstance(field_type, TaskFieldDefinitionType) else field_type


class InitialState(BaseModel, CamelAlias):
    name: str | TaskStateDefinition
    required_fields: list[str | TaskFieldDefinition] | None = []

    @field_serializer("name")
    def name_serializer(self, name: str | TaskStateDefinition):
        return name.name if isinstance(name, TaskStateDefinition) else name

    @field_serializer("required_fields")
    def req_fields(self, required_fields) -> list[str] | None:
        return [f.name if isinstance(f, TaskFieldDefinition) else f for f in required_fields]


class TriggerDefinition(BaseModel):
    name: str
    type: str

    @model_serializer()
    def serialize_model(self):
        return {"name": self.name, "trigger": {"type": self.type}}


class FieldMapping(BaseModel, CamelAlias):
    map_from: str | TaskFieldDefinition | None = None
    set_to: Any = None

    @field_serializer("map_from")
    def map_serializer(self, value: str | TaskFieldDefinition | None) -> Any | None:
        return value.name if isinstance(value, TaskFieldDefinition) else value


class ChildTaskConfiguration(BaseModel, CamelAlias):
    task_definition: TaskDefinitionResource | TaskDefinitionRef = Field(
        serialization_alias="taskDefinitionId"
    )
    task_definition_as_at: str | datetime | None = None
    initial_trigger: str | TriggerDefinition | None = None
    child_task_fields: dict[str | TaskFieldDefinition, FieldMapping] | None = None
    map_stacking_key_from: str | TaskFieldDefinition | None = None

    @field_serializer("task_definition")
    def task_definition_id(
        self, task_definition: TaskDefinitionResource | TaskDefinitionRef
    ) -> dict[str, str]:
        return {"scope": task_definition.scope, "code": task_definition.code}

    @field_serializer("task_definition_as_at")
    def task_def_as_at(self, task_as_at: str | datetime | None) -> str | None:
        return task_as_at.isoformat() if isinstance(task_as_at, datetime) else task_as_at

    @field_serializer("initial_trigger")
    def trigger(self, initial_trigger: str | TriggerDefinition | None) -> str | None:
        return (
            initial_trigger.name if isinstance(initial_trigger, TriggerDefinition) else initial_trigger
        )

    @field_serializer("map_stacking_key_from")
    def mskf(self, map_stacking_key_from: str | TaskFieldDefinition | None) -> str | None:
        return (
            map_stacking_key_from.name
            if isinstance(map_stacking_key_from, TaskFieldDefinition)
            else map_stacking_key_from
        )

    @field_serializer("child_task_fields")
    def ctf(self, child_task_fields: dict[str | TaskFieldDefinition, FieldMapping]):
        return {
            k.name if isinstance(k, TaskFieldDefinition) else k: v for k, v in child_task_fields.items()
        }


class CreateChildTasksAction(BaseModel, CamelAlias):
    type: str = Field(init=False, default="CreateChildTasks")
    child_task_configurations: list[ChildTaskConfiguration]

    def deps(self) -> list[TaskDefinitionResource | TaskDefinitionRef]:
        return [c.task_definition for c in self.child_task_configurations]


class WorkerStatusTriggers(BaseModel, CamelAlias):
    started: str | TriggerDefinition | None = None
    completed_with_results: str | TriggerDefinition | None = None
    completed_no_results: str | TriggerDefinition | None = None
    failed_to_start: str | TriggerDefinition | None = None
    failed_to_complete: str | TriggerDefinition | None = None

    @field_serializer("*")
    def serialize_fields(self, value) -> str:
        return value.name if isinstance(value, TriggerDefinition) else value


class TriggerParentTaskAction(BaseModel):
    type: str = Field(default="TriggerParentTask", init=False)
    trigger: str | TriggerDefinition

    @field_serializer("trigger")
    def trigger_serialization(self, trigger: str | TriggerDefinition) -> str:
        return trigger.name if isinstance(trigger, TriggerDefinition) else trigger


class ResultantChildTaskConfiguration(BaseModel, CamelAlias):
    child_task_configuration: ChildTaskConfiguration
    result_matching_pattern: str | None = None

    @model_serializer()
    def serialize_model(self):
        result_pattern = (
            {"resultMatchingPattern": {"filter": self.result_matching_pattern}}
            if self.result_matching_pattern
            else None
        )
        if result_pattern is None:
            return self.child_task_configuration.model_dump(by_alias=True, exclude_none=True)
        else:
            return (
                self.child_task_configuration.model_dump(by_alias=True, exclude_none=True)
                | result_pattern
            )


class RunWorkerAction(BaseModel, CamelAlias):
    type: str = Field(init=False, default="RunWorker")
    worker: WorkerResource | WorkerRef = Field(exclude=True)
    worker_as_at: str | datetime | None = None
    worker_parameters: dict[str | TaskFieldDefinition, FieldMapping] | None = None
    worker_status_triggers: WorkerStatusTriggers | None = None
    child_task_configurations: list[ResultantChildTaskConfiguration] | None = None
    # in seconds
    worker_timeout: int | None = None

    @computed_field()
    def worker_id(self) -> dict[str, str]:
        return {"scope": self.worker.scope, "code": self.worker.code}

    @field_serializer("worker_as_at")
    def worker_as_at_s(self, worker_as_at: str | datetime | None) -> str | None:
        return worker_as_at.isoformat() if isinstance(worker_as_at, datetime) else worker_as_at

    @field_serializer("worker_parameters")
    def worker_params(self, worker_parameters: dict[str | TaskFieldDefinition, FieldMapping]):
        return {
            k.name if isinstance(k, TaskFieldDefinition) else k: v for k, v in worker_parameters.items()
        }

    def deps(self) -> list[Any]:
        child_tasks = self.child_task_configurations if self.child_task_configurations else []
        return [self.worker] + [c.child_task_configuration.task_definition for c in child_tasks]


class ActionDefinition(BaseModel, CamelAlias):
    name: str
    action_details: CreateChildTasksAction | RunWorkerAction | TriggerParentTaskAction
    run_as_user_id: str | identity.UserResource | identity.UserRef | None = None

    @field_serializer("run_as_user_id")
    def user_id(
        self, run_as_user_id: str | identity.UserResource | identity.UserRef | None
    ) -> str | None:
        return run_as_user_id if isinstance(run_as_user_id, str | None) else run_as_user_id.user_id

    def deps(self) -> list[Any]:
        result = []
        if isinstance(self.run_as_user_id, identity.UserResource | identity.UserRef):
            result.append(self.run_as_user_id)
        if isinstance(self.action_details, CreateChildTasksAction | RunWorkerAction):
            result.extend(self.action_details.deps())
        return result


class TaskTransitionDefinition(BaseModel, CamelAlias):
    from_state: str | TaskStateDefinition
    to_state: str | TaskStateDefinition
    trigger: str | TriggerDefinition
    guard: str | None = None
    action: str | ActionDefinition | None = None

    @field_serializer("from_state", "to_state", "trigger", "action")
    def state_serializer(
        self, value: str | TaskStateDefinition | TriggerDefinition | ActionDefinition
    ) -> str:
        return (
            value.name
            if isinstance(value, (TaskStateDefinition, TriggerDefinition, ActionDefinition))
            else value
        )

    def deps(self):
        return self.action.deps() if isinstance(self.action, ActionDefinition) else []


@register_resource()
class EventHandlerRef(BaseModel, Ref):
    """Reference an existing event handler

    Example
    ----------
    >>> from fbnconfig import workflows
    >>> workflows.EventHandlerRef(
    ...  id="reconciliation-event-handler",
    ...  scope="reconciliation",
    ...  code="start-event")
    """

    id: str = Field(exclude=True)
    scope: str
    code: str

    def attach(self, client) -> None:
        try:
            client.get(f"/workflow/api/eventhandlers/{self.scope}/{self.code}")
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Event handler {self.scope}/{self.code} does not exist")
            else:
                raise ex


@register_resource()
class EventHandlerResource(BaseModel, Resource):
    """
    Create an event handler

    Example
    -------
    >>> from fbnconfig import workflows
    >>> event_handler = EventHandlerResource(
    >>> id="event_handler_id",
    >>> scope="scope",
    >>> code="code",
    >>> display_name="event_handler_name",
    >>> description="event_handler_description",
    >>> status="initial_status",
    >>> event_matching_pattern=EventMatchingPattern(event_type="AllocationCreated",filter=None),
    >>> run_as_user_id=EventHandlerMapping(set_to="ExampleUser"),
    >>> task_definition_id=TaskDefinitionRef(
    >>>         id="task_definition_id",
    >>>         scope="scope",
    >>>         code="task_def_code"),
    >>> task_activity=CreateNewTaskActivity(type="CreateNewTask", initial_trigger="Start")
    >>> )
    """

    id: str = Field(exclude=True)
    scope: str = Field(exclude=True)
    code: str = Field(exclude=True)
    display_name: str
    description: str | None = None
    status: str | EventStatus
    event_matching_pattern: EventMatchingPattern
    run_as_user_id: EventHandlerMapping
    task_definition: TaskDefinitionResource | TaskDefinitionRef = Field(
        serialization_alias="taskDefinitionId"
    )
    task_definition_as_at: datetime | None = None
    task_activity: CreateNewTaskActivity | UpdateMatchingTasksActivity

    @computed_field(alias="id")
    def event_handler_id(self) -> dict[str, str]:
        return {"scope": self.scope, "code": self.code}

    @field_serializer("task_definition")
    def task_definition_id(
        self, task_definition: TaskDefinitionResource | TaskDefinitionRef
    ) -> dict[str, str]:
        return {"scope": task_definition.scope, "code": task_definition.code}

    def __get_content_hash__(self) -> str:
        dump = self.model_dump(
            mode="json", exclude_none=True, by_alias=True, exclude={"event_handler_id"}
        )
        return hashlib.sha256(json.dumps(dump, sort_keys=True).encode()).hexdigest()

    def read(self, client: httpxClient, old_state: SimpleNamespace) -> None | dict[str, Any]:
        scope = old_state.scope
        code = old_state.code

        return client.get(f"/workflow/api/eventhandlers/{scope}/{code}").json()

    def create(self, client: httpxClient) -> dict[str, Any] | None:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        remote = client.post("/workflow/api/eventhandlers", json=desired).json()

        return {
            "id": self.id,
            "scope": self.scope,
            "code": self.code,
            "source_version": self.__get_content_hash__(),
            "remote_version": f"{remote['version']['asAtVersionNumber']}",
        }

    def update(self, client: httpxClient, old_state) -> dict[str, Any] | None:
        if [self.scope, self.code] != [old_state.scope, old_state.code]:
            self.delete(client, old_state)
            return self.create(client)
        remote = self.read(client, old_state) or {}
        remote_version = f"{remote['version']['asAtVersionNumber']}"

        desired = self.model_dump(
            mode="json", exclude_none=True, by_alias=True, exclude={"event_handler_id"}
        )

        source_version = self.__get_content_hash__()

        if source_version == old_state.source_version and remote_version == old_state.remote_version:
            return None

        updated = client.put(
            f"/workflow/api/eventhandlers/{self.scope}/{self.code}", json=desired
        ).json()

        return {
            "id": self.id,
            "scope": self.scope,
            "code": self.code,
            "source_version": source_version,
            "remote_version": f"{updated['version']['asAtVersionNumber']}",
        }

    @staticmethod
    def delete(client: httpxClient, old_state) -> None:
        client.delete(f"/workflow/api/eventhandlers/{old_state.scope}/{old_state.code}")

    def deps(self) -> list[TaskDefinitionResource | TaskDefinitionRef]:
        return [self.task_definition]
