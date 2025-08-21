import os
from types import SimpleNamespace

from pytest import fixture

import fbnconfig
import tests.integration.customentity as example
from tests.integration.generate_test_name import gen

if os.getenv("FBN_ACCESS_TOKEN") is None or os.getenv("LUSID_ENV") is None:
    raise (
        RuntimeError("Both FBN_ACCESS_TOKEN and LUSID_ENV variables need to be set to run these tests")
    )

lusid_env = os.environ["LUSID_ENV"]
token = os.environ["FBN_ACCESS_TOKEN"]
host_vars = {}
client = fbnconfig.create_client(lusid_env, token)


@fixture(scope="module")
def setup_deployment():
    deployment_name = gen("ce")
    print(f"\nRunning for deployment {deployment_name}...")
    yield SimpleNamespace(name=deployment_name)
    # Can't teardown as CE doesn't support delete


def test_create(setup_deployment):
    fbnconfig.deploy(example.configure(setup_deployment), lusid_env, token)
    res = client.get(f"/api/api/customentities/entitytypes/~{setup_deployment.name}").json()
    assert res is not None


def test_nochange(setup_deployment):
    fbnconfig.deploy(example.configure(setup_deployment), lusid_env, token)
    update = fbnconfig.deploy(example.configure(setup_deployment), lusid_env, token)
    assert [a.change for a in update if a.type == "EntityTypeResource"] == ["nochange"]
