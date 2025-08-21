from fbnconfig import Deployment, workspace


def configure(env):
    deployment_name = getattr(env, "name", "workspace_example")
    wksp = workspace.WorkspaceResource(
        id="wk1",
        visibility=workspace.Visibility.SHARED,
        name=deployment_name,
        description="workspace number one",
    )
    item1 = workspace.WorkspaceItemResource(
        id="item1",
        workspace=wksp,
        group="group1",
        name="item1",
        description="item one version two",
        type="lusid-web-dashboard",
        format=1,
        content={"msg": "some text"},
    )
    item2 = workspace.WorkspaceItemResource(
        id="item2",
        workspace=wksp,
        group="group1",
        name="item2",
        description="item one version two",
        format=1,
        type="lusid-web-dashboard",
        content={"msg": "some text", "foo": 10},
    )
    return Deployment(deployment_name, [item1, item2])
