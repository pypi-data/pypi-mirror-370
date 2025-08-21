import os
from types import SimpleNamespace

import pytest
from httpx import HTTPStatusError
from pytest import fixture

import fbnconfig
import tests.integration.workspace as workspace
from tests.integration.generate_test_name import gen

if os.getenv("FBN_ACCESS_TOKEN") is None or os.getenv("LUSID_ENV") is None:
    raise (
        RuntimeError("Both FBN_ACCESS_TOKEN and LUSID_ENV variables need to be set to run these tests")
    )

lusid_env = os.environ["LUSID_ENV"]
token = os.environ["FBN_ACCESS_TOKEN"]
host_vars = {}
client = fbnconfig.create_client(lusid_env, token)


@fixture
def setup_deployment():
    deployment_name = gen("workspace_example")
    print(f"\nRunning for deployment {deployment_name}...")
    yield SimpleNamespace(name=deployment_name)
    # Teardown: Clean up resources (if any) after the test
    print("\nTearing down resources...")
    fbnconfig.deploy(fbnconfig.Deployment(deployment_name, []), lusid_env, token)


def test_teardown(setup_deployment):
    # create first
    fbnconfig.deploy(workspace.configure(setup_deployment), lusid_env, token)
    fbnconfig.deploy(fbnconfig.Deployment(setup_deployment.name, []), lusid_env, token)
    with pytest.raises(HTTPStatusError) as error:
        client.get(f"/api/api/workspaces/shared/{setup_deployment.name}")
    assert error.value.response.status_code == 404


def test_create(setup_deployment):
    fbnconfig.deploy(workspace.configure(setup_deployment), lusid_env, token)
    search = client.get(f"/api/api/workspaces/shared/{setup_deployment.name}/items/group1/item1")
    assert search.status_code == 200


def test_update(setup_deployment):
    fbnconfig.deploy(workspace.configure(setup_deployment), lusid_env, token)
    fbnconfig.deploy(workspace.configure(setup_deployment), lusid_env, token)
    search = client.get(f"/api/api/workspaces/shared/{setup_deployment.name}/items/group1/item1")
    assert search.status_code == 200
