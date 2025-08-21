import os
from types import SimpleNamespace

from pytest import fixture

import fbnconfig
from fbnconfig import reference_list as rl
from tests.integration.generate_test_name import gen

if os.getenv("FBN_ACCESS_TOKEN") is None or os.getenv("LUSID_ENV") is None:
    raise (
        RuntimeError("Both FBN_ACCESS_TOKEN and LUSID_ENV variables need to be set to run these tests")
    )

lusid_env = os.environ["LUSID_ENV"]
token = os.environ["FBN_ACCESS_TOKEN"]
host_vars = {}
client = fbnconfig.create_client(lusid_env, token)


@fixture()
def base_resources(setup_deployment):
    deployment_name = setup_deployment.name
    # Create a simple string list reference list
    string_reflist = rl.ReferenceListResource(
        id="string_reflist",
        scope=deployment_name,
        code="string-list-1",
        name="Test String Reference List",
        description="A test reference list with string values",
        tags=["test", "integration"],
        reference_list=rl.StringList(values=["value1", "value2", "value3"])
    )
    # Create a decimal list reference list
    decimal_reflist = rl.ReferenceListResource(
        id="decimal_reflist",
        scope=deployment_name,
        code="decimal-list-1",
        name="Test Decimal Reference List",
        description="A test reference list with decimal values",
        reference_list=rl.DecimalList(values=[1.5, 2.75, 3.0])
    )
    # Create an address key list reference list
    address_reflist = rl.ReferenceListResource(
        id="address_reflist",
        scope=deployment_name,
        code="address-key-list-1",
        name="Test Address Key Reference List",
        reference_list=rl.AddressKeyList(values=["Portfolio/Name", "Portfolio/Currency"])
    )
    return [string_reflist, decimal_reflist, address_reflist]


@fixture(scope="module")
def setup_deployment():
    deployment_name = gen("reference_list")
    print(f"\nRunning for deployment {deployment_name}...")
    yield SimpleNamespace(name=deployment_name)
    # Clean up reference lists after tests
    try:
        client.delete(f"/api/api/referencelists/{deployment_name}/string-list-1")
        client.delete(f"/api/api/referencelists/{deployment_name}/decimal-list-1")
        client.delete(f"/api/api/referencelists/{deployment_name}/address-key-list-1")
    except Exception:
        pass  # Ignore cleanup errors


def test_create(setup_deployment, base_resources):
    deployment = fbnconfig.Deployment(setup_deployment.name, base_resources)
    fbnconfig.deploy(deployment, lusid_env, token)
    # Verify string reference list was created
    string_response = client.get(f"/api/api/referencelists/{setup_deployment.name}/string-list-1").json()
    assert string_response["id"]["scope"] == setup_deployment.name
    assert string_response["id"]["code"] == "string-list-1"
    assert string_response["name"] == "Test String Reference List"
    assert string_response["description"] == "A test reference list with string values"
    assert string_response["tags"] == ["test", "integration"]
    assert string_response["referenceList"]["values"] == ["value1", "value2", "value3"]
    assert string_response["referenceList"]["referenceListType"] == "StringList"
    # Verify decimal reference list was created
    decimal_response = client.get(
        f"/api/api/referencelists/{setup_deployment.name}/decimal-list-1"
    ).json()
    assert decimal_response["id"]["scope"] == setup_deployment.name
    assert decimal_response["id"]["code"] == "decimal-list-1"
    assert decimal_response["name"] == "Test Decimal Reference List"
    assert decimal_response["referenceList"]["values"] == [1.5, 2.75, 3.0]
    assert decimal_response["referenceList"]["referenceListType"] == "DecimalList"
    # Verify address key reference list was created
    address_response = client.get(
        f"/api/api/referencelists/{setup_deployment.name}/address-key-list-1"
    ).json()
    assert address_response["id"]["scope"] == setup_deployment.name
    assert address_response["id"]["code"] == "address-key-list-1"
    assert address_response["name"] == "Test Address Key Reference List"
    assert address_response["referenceList"]["values"] == ["Portfolio/Name", "Portfolio/Currency"]
    assert address_response["referenceList"]["referenceListType"] == "AddressKeyList"


def test_nochange(setup_deployment, base_resources):
    # given we have deployed the base case
    deployment = fbnconfig.Deployment(setup_deployment.name, base_resources)
    fbnconfig.deploy(deployment, lusid_env, token)
    # when we apply it again
    update = fbnconfig.deploy(deployment, lusid_env, token)
    # then there are no changes
    ref_list_changes = [a.change for a in update if a.type == "ReferenceListResource"]
    assert ref_list_changes == ["nochange", "nochange", "nochange"]


def test_teardown(setup_deployment, base_resources):
    deployment_name = setup_deployment.name
    # given we have deployed the base case
    deployment = fbnconfig.Deployment(deployment_name, base_resources)
    fbnconfig.deploy(deployment, lusid_env, token)
    # when we remove all the resources
    empty = fbnconfig.Deployment(deployment_name, [])
    update = fbnconfig.deploy(empty, lusid_env, token)
    # then there are no changes
    ref_list_changes = [a.change for a in update if a.type == "ReferenceListResource"]
    assert ref_list_changes == ["remove", "remove", "remove"]


def test_update(setup_deployment, base_resources):
    deployment_name = setup_deployment.name
    # Given we have deployed the base case
    initial = fbnconfig.Deployment(deployment_name, base_resources)
    fbnconfig.deploy(initial, lusid_env, token)
    # when we update a resource
    updated_resources = [
        # Update the string list with different values
        rl.ReferenceListResource(
            id="string_reflist",
            scope=deployment_name,
            code="string-list-1",
            name="Updated String Reference List",  # Changed name
            description="An updated test reference list with string values",  # Changed description
            tags=["test", "integration", "updated"],  # Added tag
            reference_list=rl.StringList(
                values=["newvalue1", "newvalue2"]
            )  # Changed values
        ),
        # Keep decimal list the same
        rl.ReferenceListResource(
            id="decimal_reflist",
            scope=deployment_name,
            code="decimal-list-1",
            name="Test Decimal Reference List",
            description="A test reference list with decimal values",
            reference_list=rl.DecimalList(values=[1.5, 2.75, 3.0])
        ),
        # Keep address key list the same
        rl.ReferenceListResource(
            id="address_reflist",
            scope=deployment_name,
            code="address-key-list-1",
            name="Test Address Key Reference List",
            reference_list=rl.AddressKeyList(values=["Portfolio/Name", "Portfolio/Currency"])
        ),
    ]
    # and deploy it
    updated_deployment = fbnconfig.Deployment(deployment_name, updated_resources)  # type: ignore
    update = fbnconfig.deploy(updated_deployment, lusid_env, token)
    # then we expect only the modified resource to change
    ref_list_changes = [a.change for a in update if a.type == "ReferenceListResource"]
    assert ref_list_changes == ["update", "nochange", "nochange"]
    # and it has the new values
    updated_response = client.get(
        f"/api/api/referencelists/{deployment_name}/string-list-1"
    ).json()
    assert updated_response["name"] == "Updated String Reference List"
    assert updated_response["description"] == "An updated test reference list with string values"
    assert updated_response["tags"] == ["test", "integration", "updated"]
    assert updated_response["referenceList"]["values"] == ["newvalue1", "newvalue2"]
