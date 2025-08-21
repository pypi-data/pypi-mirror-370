import json
from types import SimpleNamespace
from typing import List, NamedTuple, Union

import httpx

from fbnconfig import http_client, log
from fbnconfig.resource_abc import Ref, Resource, get_resource_class, get_resource_type  # noqa: F401

Deployment = NamedTuple("Deployment", [("id", str), ("resources", List[Union[Resource, Ref]])])
deployments = []

Action = NamedTuple("Action", [("id", str), ("type", str), ("change", str)])


def deployment(id, resources):
    d = Deployment(id, resources)
    deployments.append(d)


def recurse_resources(resources):
    seen = dict()
    ordered = []

    def helper(items):
        for res in items:
            deps = res.deps()
            if len(deps) > 0:
                helper(deps)
            if seen.get(res.id, None) is None:
                seen[res.id] = id(res)
                ordered.append(res)
            elif id(res) != seen[res.id]:
                raise RuntimeError(f"Resource ID: {res.id} has been used on more than one resource")

    helper(resources)
    return ordered


def sort_deployed(entries):
    seen = set()
    ordered = []

    def helper(items):
        for e in items:
            dep_ids = e.dependencies
            if len(dep_ids) > 0:
                deps = [e for e in entries if e.resource_id in dep_ids]
                helper(deps)
            if e.resource_id not in seen:
                seen.add(e.resource_id)
                ordered.append(e)

    helper(entries)
    return ordered


def run(client: httpx.Client, deployment) -> List[Action]:
    actions = []
    resources = deployment.resources
    all_resources = recurse_resources(resources)
    deploy_state = log.list_resources_for_deployment(client, deployment.id)
    for resource in all_resources:
        if isinstance(resource, Ref):
            resource.attach(client)
            actions.append(Action(id=resource.id, type=get_resource_type(resource), change="attach"))
            print("attach", get_resource_type(resource))
            continue
        match = [e for e in deploy_state if e.resource_id == resource.id]
        if len(match) == 0:
            print("deploy: create", get_resource_type(resource), resource.id)
            state = resource.create(client)
            log.record(client, deployment.id, resource, state)
            actions.append(Action(id=resource.id, type=get_resource_type(resource), change="create"))
        else:
            print("deploy: update", get_resource_type(resource), resource.id)
            state = resource.update(client, match[0].state)
            if state is not None:
                log.record(client, deployment.id, resource, state)
                actions.append(Action(id=resource.id, type=get_resource_type(resource), change="update"))
            else:
                print("deploy: nochange", get_resource_type(resource), resource.id)
                actions.append(
                    Action(id=resource.id, type=get_resource_type(resource), change="nochange")
                )
    for deployed in reversed(sort_deployed(deploy_state)):
        matching_resource = [e for e in all_resources if e.id == deployed.resource_id]
        if len(matching_resource) == 0:
            klas = get_resource_class(deployed.resource_type)
            print("deploy: remove", deployed.resource_type, deployed.resource_id)
            klas.delete(client, deployed.state)
            log.remove(client, deployment.id, deployed.resource_id)
            actions.append(Action(id=deployed.resource_id, type=deployed.resource_type, change="remove"))
    return actions


# called as a library
def deploy(deployment: Deployment, lusid_url: str, access_token: str) -> List[Action]:
    client = http_client.create_client(lusid_url, access_token)
    return run(client, deployment)


def load_vars(vars_file):
    if vars_file:
        host_vars = SimpleNamespace(**json.load(vars_file))
    else:
        host_vars = SimpleNamespace()
    return host_vars
