import os
from types import SimpleNamespace

from pytest import fixture

import fbnconfig
import tests.integration.drive as drive
from tests.integration.generate_test_name import gen

if os.getenv("FBN_ACCESS_TOKEN") is None or os.getenv("LUSID_ENV") is None:
    raise (
        RuntimeError("Both FBN_ACCESS_TOKEN and LUSID_ENV variables need to be set to run these tests")
    )

lusid_env = os.environ["LUSID_ENV"]
token = os.environ["FBN_ACCESS_TOKEN"]
host_vars = {}


@fixture(scope="module")
def setup_deployment():
    deployment_name = gen("folders")
    print(f"\nRunning for deployment {deployment_name}...")
    yield SimpleNamespace(name=deployment_name, base_dir=deployment_name)
    # Teardown: Clean up resources (if any) after the test
    print("\nTearing down resources...")
    fbnconfig.deploy(fbnconfig.Deployment(deployment_name, []), lusid_env, token)


def test_teardown(setup_deployment):
    fbnconfig.deploy(drive.configure(setup_deployment), lusid_env, token)
    fbnconfig.deploy(fbnconfig.Deployment(setup_deployment.name, []), lusid_env, token)
    client = fbnconfig.create_client(lusid_env, token)
    search = client.post("/drive/api/search/", json={"withPath": "/", "name": setup_deployment.name})
    assert search.json()["values"] == []


def test_create(setup_deployment):
    fbnconfig.deploy(drive.configure(setup_deployment), lusid_env, token)

    client = fbnconfig.create_client(lusid_env, token)
    search = client.post("/drive/api/search/", json={"withPath": "/", "name": setup_deployment.name})
    assert len(search.json()["values"]) == 1


def test_update(setup_deployment):
    fbnconfig.deploy(drive.configure(setup_deployment), lusid_env, token)
    client = fbnconfig.create_client(lusid_env, token)
    search = client.post("/drive/api/search/", json={"withPath": "/", "name": setup_deployment.name})
    assert len(search.json()["values"]) == 1
