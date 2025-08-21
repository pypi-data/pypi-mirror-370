import os

import fbnconfig
import tests.integration.application as application

if os.getenv("FBN_ACCESS_TOKEN") is None or os.getenv("LUSID_ENV") is None:
    raise (
        RuntimeError("Both FBN_ACCESS_TOKEN and LUSID_ENV variables need to be set to run these tests")
    )

lusid_env = os.environ["LUSID_ENV"]
token = os.environ["FBN_ACCESS_TOKEN"]
host_vars = {}


def test_teardown():
    deployment_name = application.configure({}).id
    fbnconfig.deploy(fbnconfig.Deployment(deployment_name, []), lusid_env, token)
    client = fbnconfig.create_client(lusid_env, token)
    matches = get_applications_by_client_id(client, "robTest-app-client")
    assert len(matches) == 0


def test_create():
    fbnconfig.deploy(application.configure(host_vars), lusid_env, token)
    client = fbnconfig.create_client(lusid_env, token)
    matches = get_applications_by_client_id(client, "robTest-app-client")
    assert len(matches) == 1
    app = matches[0]
    assert app["displayName"] == "robTest Application"
    assert app["type"] == "Native"


def test_update():
    fbnconfig.deploy(application.configure(host_vars), lusid_env, token)
    client = fbnconfig.create_client(lusid_env, token)
    matches = get_applications_by_client_id(client, "robTest-app-client")
    assert len(matches) == 1
    app = matches[0]
    assert app["displayName"] == "robTest Application"
    assert app["type"] == "Native"


def get_applications_by_client_id(client, client_id):
    get = client.request("get", "/identity/api/applications")
    get.raise_for_status()
    applications = get.json()
    return [app for app in applications if app["clientId"] == client_id]
