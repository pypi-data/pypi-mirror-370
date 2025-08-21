import os
from types import SimpleNamespace

import pytest
from httpx import HTTPStatusError
from pytest import fixture

import fbnconfig
import tests.integration.transaction_configuration as transaction_config
from tests.integration.generate_test_name import gen

if os.getenv("FBN_ACCESS_TOKEN") is None or os.getenv("LUSID_ENV") is None:
    raise (
        RuntimeError("Both FBN_ACCESS_TOKEN and LUSID_ENV variables need to be set to run these tests")
    )

lusid_env = os.environ["LUSID_ENV"]
token = os.environ["FBN_ACCESS_TOKEN"]
print(f"{lusid_env} / {token}")
host_vars = {}
client = fbnconfig.create_client(lusid_env, token)


@fixture(scope="module")
def setup_deployment():
    deployment_name = gen("transaction_configuration")
    print(f"\nRunning for deployment {deployment_name}...")
    yield SimpleNamespace(name=deployment_name)
    # Teardown: Clean up resources (if any) after the test
    print("\nTearing down resources...")
    fbnconfig.deploy(fbnconfig.Deployment(deployment_name, []), lusid_env, token)


def test_teardown_side(setup_deployment):
    # create first
    fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    fbnconfig.deploy(fbnconfig.Deployment(setup_deployment.name, []), lusid_env, token)
    with pytest.raises(HTTPStatusError) as error:
        client.get(
            "/api/api/transactionconfiguration/sides/Side1", params={"scope": setup_deployment.name}
        )
        assert error.value.response.status_code == 404


def test_create_side(setup_deployment):
    fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    search = client.get(
        "/api/api/transactionconfiguration/sides/Side1", params={"scope": setup_deployment.name}
    )
    assert search.status_code == 200


def test_nochange_side(setup_deployment):
    fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    update = fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    assert [a.change for a in update if a.type == "SideResource"] == ["nochange", "nochange"]


def test_teardown_transaction_type(setup_deployment):
    fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    fbnconfig.deploy(fbnconfig.Deployment(setup_deployment.name, []), lusid_env, token)
    with pytest.raises(HTTPStatusError) as error:
        client.get(
            "/api/api/transactionconfiguration/types/default/Buy",
            params={"scope": setup_deployment.name},
        )
        assert error.value.response.status_code == 404


def test_create_transaction_type(setup_deployment):
    fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    search = client.get(
        "/api/api/transactionconfiguration/types/default/Buy", params={"scope": setup_deployment.name}
    )
    assert search.status_code == 200


def test_nochange_transaction_type(setup_deployment):
    fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    update = fbnconfig.deploy(transaction_config.configure(setup_deployment), lusid_env, token)
    assert [a.change for a in update if a.type == "TransactionTypeResource"] == ["nochange"]
