import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import access

TEST_BASE = "https://foo.lusid.com"


def response_hook(response: httpx.Response):
    response.read()
    response.raise_for_status()


@pytest.mark.respx(base_url=TEST_BASE)
class DescribePolicyRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    @staticmethod
    def test_scope_default():
        # when scope is omitted
        sut = access.PolicyRef(id="one", code="cd")
        # then it uses "default"
        assert sut.scope == "default"

    def test_attach_when_present(self, respx_mock):
        # given that the remote definition exists
        respx_mock.get("/access/api/policies/pol1?scope=sc1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = access.PolicyRef(id="one", scope="sc1", code="pol1")
        # when we call attach
        sut.attach(client)
        # then a get request was made and no exception raised

    def test_attach_when_missing(self, respx_mock):
        # given the remote does not exist
        respx_mock.get("/access/api/policies/pol1?scope=sc1").mock(
            return_value=httpx.Response(404, json={})
        )
        client = self.client
        sut = access.PolicyRef(id="one", scope="sc1", code="pol1")
        # when we call attach an exception is raised
        with pytest.raises(RuntimeError) as ex:
            sut.attach(client)
        assert "Policy sc1/pol1 not found" in str(ex.value)

    def test_attach_when_http_error(self, respx_mock):
        # given the server returns an error
        respx_mock.get("/access/api/policies/pol1?scope=sc1").mock(
            return_value=httpx.Response(500, json={})
        )
        client = self.client
        sut = access.PolicyRef(id="one", scope="sc1", code="pol1")
        # when we call attach an exception is raised
        with pytest.raises(httpx.HTTPError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribePolicy:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    @pytest.fixture
    def stock_policy_resource(self):
        # uses new style selector definition: List[Selector]
        return access.PolicyResource(
            id="policy1",
            code="a_policy",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.IdSelector(
                    name="banjo",
                    description="whatever",
                    identifier={"scope": "w", "code": "y"},
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )

    def test_create(self, respx_mock):
        respx_mock.post("/access/api/policies").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        # given no policies exist yet
        # when we create one
        sut = access.PolicyResource(
            id="policy1",
            code="a_policy",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.IdSelector(
                    name="banjo",
                    description="whatever",
                    identifier={"scope": "w", "code": "y"},
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )
        state = sut.create(client)
        # then the state is returned
        assert state["id"] == "policy1"
        assert state["code"] == "a_policy"
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/policies"
        assert json.loads(request.content) == {
            "applications": ["lusid"],
            "code": "a_policy",
            "description": "policy description",
            "grant": "Allow",
            "selectors": [
                {
                    "idSelectorDefinition": {
                        "actions": [{"activity": "execute", "entity": "Feature", "scope": "actscope"}],
                        "description": "whatever",
                        "identifier": {"code": "y", "scope": "w"},
                        "name": "banjo",
                    }
                }
            ],
            "when": {"activate": "2024-08-31T18:00:00.0000000+00:00"},
        }

    def test_create_matchall_selector(self, respx_mock):
        respx_mock.post("/access/api/policies").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        # given no policies exist yet
        # when we create one with a matchall selector
        sut = access.PolicyResource(
            id="policy1",
            code="a_policy",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.MatchAllSelector(
                    name="banjo",
                    description="whatever",
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )
        state = sut.create(client)
        # then the state is returned
        assert state["id"] == "policy1"
        assert state["code"] == "a_policy"
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/policies"
        assert json.loads(request.content) == {
            "applications": ["lusid"],
            "code": "a_policy",
            "description": "policy description",
            "grant": "Allow",
            "selectors": [
                {
                    "matchAllSelectorDefinition": {
                        "actions": [{"activity": "execute", "entity": "Feature", "scope": "actscope"}],
                        "description": "whatever",
                        "name": "banjo",
                    }
                }
            ],
            "when": {"activate": "2024-08-31T18:00:00.0000000+00:00"},
        }

    def test_create_metadata_selector(self, respx_mock):
        respx_mock.post("/access/api/policies").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        # given no policies exist yet
        # when we create one with a metadata selector
        sut = access.PolicyResource(
            id="policy1",
            code="a_policy",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.MetadataSelector(
                    name="banjo",
                    description="whatever",
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                    expressions=[
                        access.MetadataExpression(
                            metadata_key="foo", operator="Equals", text_value="bingo"
                        )
                    ],
                )
            ],
        )
        state = sut.create(client)
        # then the state is returned
        assert state["id"] == "policy1"
        assert state["code"] == "a_policy"
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/policies"
        assert json.loads(request.content) == {
            "applications": ["lusid"],
            "code": "a_policy",
            "description": "policy description",
            "grant": "Allow",
            "selectors": [
                {
                    "metadataSelectorDefinition": {
                        "actions": [{"activity": "execute", "entity": "Feature", "scope": "actscope"}],
                        "description": "whatever",
                        "name": "banjo",
                        "expressions": [
                            {"metadataKey": "foo", "operator": "Equals", "textValue": "bingo"}
                        ],
                    }
                }
            ],
            "when": {"activate": "2024-08-31T18:00:00.0000000+00:00"},
        }

    def test_create_policy_selector(self, respx_mock):
        respx_mock.post("/access/api/policies").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        # given no policies exist yet
        # when we create one with a policy selector and a nested matchall
        inner_selector = access.MatchAllSelector(
            name="banjo",
            description="whatever",
            actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
        )
        sut = access.PolicyResource(
            id="policy1",
            code="a_policy",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.PolicySelector(
                    name="banjo",
                    description="whatever",
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                    identity_restriction={"id": "value"},
                    restriction_selectors=[inner_selector],
                )
            ],
        )
        state = sut.create(client)
        # then the state is returned
        assert state["id"] == "policy1"
        assert state["code"] == "a_policy"
        # and a create request was sent including the inner selector
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/policies"
        assert json.loads(request.content) == {
            "applications": ["lusid"],
            "code": "a_policy",
            "description": "policy description",
            "grant": "Allow",
            "selectors": [
                {
                    "policySelectorDefinition": {
                        "actions": [{"activity": "execute", "entity": "Feature", "scope": "actscope"}],
                        "description": "whatever",
                        "name": "banjo",
                        "identityRestriction": {"id": "value"},
                        "restrictionSelectors": [
                            {
                                "matchAllSelectorDefinition": {
                                    "actions": [
                                        {"activity": "execute", "entity": "Feature", "scope": "actscope"}
                                    ],
                                    "description": "whatever",
                                    "name": "banjo",
                                }
                            }
                        ],
                    }
                }
            ],
            "when": {"activate": "2024-08-31T18:00:00.0000000+00:00"},
        }

    @pytest.fixture
    def read_policy_response(self):
        return {
            "applications": ["lusid"],
            "id": {
                "code": "a_policy_code",
                "scope": "default",
            },  # get returns an ID where post takes a code only
            "description": "policy description",
            "grant": "Allow",
            "selectors": [
                {
                    "idSelectorDefinition": {
                        "actions": [{"activity": "execute", "entity": "Feature", "scope": "actscope"}],
                        "description": "whatever",
                        "identifier": {"code": "y", "scope": "w"},
                        "name": "banjo",
                    }
                }
            ],
            "when": {
                "activate": "2024-08-31T18:00:00.0000000+00:00",
                "deactivate": "99999-12-31T18:00:00.0000000+00:00",
            },
            "links": {},
        }

    def test_update_no_changes(self, respx_mock, read_policy_response):
        # given the policy exists
        respx_mock.get("/access/api/policies/a_policy_code").mock(
            side_effect=[httpx.Response(200, json=read_policy_response)]
        )
        # and the desired is the same as the existing
        sut = access.PolicyResource(
            id="policy1",
            code="a_policy_code",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.IdSelector(
                    name="banjo",
                    description="whatever",
                    identifier={"scope": "w", "code": "y"},
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )
        # when we update
        log = sut.update(self.client, SimpleNamespace(code="a_policy_code", id="x"))
        # then there is no change and the log remains as is
        assert log is None
        # and no put request was made

    def test_update_modify_description(self, respx_mock, read_policy_response):
        # given the policy exists with a description = "policy description"
        respx_mock.get("/access/api/policies/a_policy_code").mock(
            side_effect=[httpx.Response(200, json=read_policy_response)]
        )
        respx_mock.put("/access/api/policies/a_policy_code").mock(
            side_effect=[httpx.Response(200, json={})]
        )
        # and the desired has a different description
        sut = access.PolicyResource(
            id="policy1",
            code="a_policy_code",
            description="a different policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.IdSelector(
                    name="banjo",
                    description="whatever",
                    identifier={"scope": "w", "code": "y"},
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )
        # when we update
        log = sut.update(self.client, SimpleNamespace(code="a_policy_code", id="x"))
        # the log is returned (but unchanged)
        assert log == {"code": "a_policy_code", "id": "policy1"}
        # and a put request was made to update the policy
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/access/api/policies/a_policy_code"
        assert json.loads(request.content) == {
            "applications": ["lusid"],
            "description": "a different policy description",
            "grant": "Allow",
            "selectors": [
                {
                    "idSelectorDefinition": {
                        "actions": [{"activity": "execute", "entity": "Feature", "scope": "actscope"}],
                        "description": "whatever",
                        "identifier": {"code": "y", "scope": "w"},
                        "name": "banjo",
                    }
                }
            ],
            "when": {"activate": "2024-08-31T18:00:00.0000000+00:00"},
        }

    def test_deps(self, stock_policy_resource):
        # policy doesn't have any deps
        sut = stock_policy_resource
        assert sut.deps() == []

    def test_delete(self, respx_mock, stock_policy_resource):
        respx_mock.delete("/access/api/policies/a_policy_code").mock(
            side_effect=[httpx.Response(200, json={})]
        )
        # given an existing policy
        # when we delete it
        old_state = SimpleNamespace(id="policy1", code="a_policy_code")
        access.PolicyResource.delete(self.client, old_state)
        # then a delete request is made
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/access/api/policies/a_policy_code"


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeRoleRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_attach_when_present(self, respx_mock):
        # given that the remote definition exists
        respx_mock.get("/access/api/roles/cd1?scope=sc1").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        sut = access.RoleRef(id="one", scope="sc1", code="cd1")
        # when we call attach
        sut.attach(client)
        # then a get request was made and no exception raised

    def test_attach_when_missing(self, respx_mock):
        # given the remote does not exist
        respx_mock.get("/access/api/roles/cd1?scope=default").mock(
            return_value=httpx.Response(404, json={})
        )
        client = self.client
        sut = access.RoleRef(id="one", code="cd1")
        # when we call attach an exception is raised
        with pytest.raises(RuntimeError) as ex:
            sut.attach(client)
        assert "Role default/cd1 not found" in str(ex.value)

    def test_attach_when_http_error(self, respx_mock):
        # given the server returns an error
        respx_mock.get("/access/api/roles/cd1?scope=sc1").mock(return_value=httpx.Response(500, json={}))
        client = self.client
        sut = access.RoleRef(id="one", scope="sc1", code="cd1")
        # when we call attach an exception is raised
        with pytest.raises(httpx.HTTPError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeRole:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    @pytest.fixture
    def stock_policy_resource(self):
        return access.PolicyResource(
            id="policy1",
            code="a_policy",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.IdSelector(
                    name="banjo",
                    description="whatever",
                    identifier={"scope": "w", "code": "y"},
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )

    def test_create_with_new_resource_request(self, respx_mock, stock_policy_resource):
        respx_mock.post("/access/api/roles").mock(return_value=httpx.Response(200, json={}))
        # given no role exists yet and we create one using the updadted RoleResourceRequest
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(
                policy_id_role_resource=access.PolicyIdRoleResource(policies=[stock_policy_resource])
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        sut.create(self.client)
        # then a post request is made
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/roles"
        assert json.loads(request.content) == {
            "code": "a_role_code",
            "permission": "Read",
            "resource": {
                "policyIdRoleResource": {
                    "policies": [{"code": "a_policy", "scope": "default"}],
                    "policyCollections": [],
                }
            },
            "when": {"activate": "2024-03-01:00:00.0000000+00:00"},
        }

    def test_create_with_nontransitive(self, respx_mock, stock_policy_resource):
        respx_mock.post("/access/api/roles").mock(return_value=httpx.Response(200, json={}))
        # given a pre-existing supervisor role
        sup = access.RoleResource(
            id="sup",
            code="supervisor",
            resource=access.RoleResourceRequest(
                policy_id_role_resource=access.PolicyIdRoleResource(policies=[])
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        # when we create a new role which references the supervisor
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(
                non_transitive_supervisor_role_resource=access.NonTransitiveSupervisorRoleResource(
                    roles=[sup]
                )
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        sut.create(self.client)
        # then a post request is made
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/roles"
        assert json.loads(request.content) == {
            "code": "a_role_code",
            "permission": "Read",
            "resource": {
                "nonTransitiveSupervisorRoleResource": {
                    "roles": [{"scope": "default", "code": "supervisor"}]
                }
            },
            "when": {"activate": "2024-03-01:00:00.0000000+00:00"},
        }

    def test_create_with_policy_collection(self, respx_mock, stock_policy_resource):
        respx_mock.post("/access/api/roles").mock(return_value=httpx.Response(200, json={}))
        respx_mock.post("/access/api/policycollections").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-inner"}})
        )
        respx_mock.post("/access/api/policycollections").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-code"}})
        )
        # given an inner collection which has already been created
        inner = access.PolicyCollectionResource(id="polly-collection", code="col-code", policies=[])
        inner.create(self.client)
        # when we create a role referenccing the collection
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(
                policy_id_role_resource=access.PolicyIdRoleResource(policy_collections=[inner])
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        sut.create(self.client)
        # then a post request is made
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/roles"
        assert json.loads(request.content) == {
            "code": "a_role_code",
            "permission": "Read",
            "resource": {
                "policyIdRoleResource": {
                    "policies": [],
                    "policyCollections": [{"scope": "default", "code": "col-code"}],
                }
            },
            "when": {"activate": "2024-03-01:00:00.0000000+00:00"},
        }

    def test_delete(self, respx_mock, stock_policy_resource):
        respx_mock.delete("/access/api/roles/a_role").mock(side_effect=[httpx.Response(200, json={})])
        # given an existing policy
        # when we delete it
        old_state = SimpleNamespace(id="role1", code="a_role")
        access.RoleResource.delete(self.client, old_state)
        # then a delete request is made
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/access/api/roles/a_role"

    @staticmethod
    def test_deps(stock_policy_resource):
        # given a role with two policy resources
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(
                policy_id_role_resource=access.PolicyIdRoleResource(policies=[stock_policy_resource])
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        # when we ask for the deps we get two back
        assert sut.deps() == [stock_policy_resource]

    def test_deps_policy_collection(self, stock_policy_resource):
        # given a role with a policy collection
        inner = access.PolicyCollectionResource(
            id="polly-collection", code="col-inner", policies=[stock_policy_resource]
        )
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(
                policy_id_role_resource=access.PolicyIdRoleResource(policy_collections=[inner])
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        # when we ask for the deps
        assert sut.deps() == [inner]

    @pytest.fixture
    def read_role_response(self):
        return {
            "id": {"scope": "default", "code": "a_role_code"},
            "when": {
                "activate": "2024-03-01:00:00.0000000+00:00",
                "deactivate": "2024-03-01:00:00.0000000+00:00",
            },
            "roleHierarchyIndex": 20,
            "permission": "Read",
            "resource": {
                "policyIdRoleResource": {"policies": [{"code": "a_policy", "scope": "default"}]}
            },
            "links": [],
        }

    def test_update_remove_policies(self, respx_mock, read_role_response):
        # given the role exists and has a policy
        respx_mock.get("/access/api/roles/a_role_code").mock(
            side_effect=[httpx.Response(200, json=read_role_response)]
        )
        respx_mock.put("/access/api/roles/a_role_code").mock(side_effect=[httpx.Response(200, json={})])
        # and the desired state is no policies
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(
                policy_id_role_resource=access.PolicyIdRoleResource(policies=[])
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        # when we update
        log = sut.update(self.client, SimpleNamespace(id="role1", code="a_role_code"))
        # then the log returned is the same
        assert log == {"code": "a_role_code", "id": "role1"}
        # and a put request to modify the role was made
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/access/api/roles/a_role_code"
        assert json.loads(request.content) == {
            "permission": "Read",  # nb no code set when its a PUT
            "resource": {"policyIdRoleResource": {"policies": [], "policyCollections": []}},
            "when": {"activate": "2024-03-01:00:00.0000000+00:00"},
        }

    def test_update_non_transitive(self, respx_mock, read_role_response):
        # given the role exists and has a policy
        respx_mock.get("/access/api/roles/a_role_code").mock(
            side_effect=[httpx.Response(200, json=read_role_response)]
        )
        respx_mock.put("/access/api/roles/a_role_code").mock(side_effect=[httpx.Response(200, json={})])
        # and there is an existing supervisor role
        sup = access.RoleResource(
            id="sup",
            code="supervisor",
            resource=access.RoleResourceRequest(
                policy_id_role_resource=access.PolicyIdRoleResource(policies=[])
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        # and the desired state only a nonTransitiveSupervisor....
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(
                non_transitive_supervisor_role_resource=access.NonTransitiveSupervisorRoleResource(
                    roles=[sup]
                )
            ),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        # when we update
        log = sut.update(self.client, SimpleNamespace(id="role1", code="a_role_code"))
        # then the log returned is the same
        assert log == {"code": "a_role_code", "id": "role1"}
        # and a put request to modify the role was made
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/access/api/roles/a_role_code"
        assert json.loads(request.content) == {
            "permission": "Read",  # nb no code set when its a PUT
            "resource": {
                "nonTransitiveSupervisorRoleResource": {
                    "roles": [{"scope": "default", "code": "supervisor"}]
                }
            },
            "when": {"activate": "2024-03-01:00:00.0000000+00:00"},
        }

    def test_update_non_transitive_ref(self, respx_mock, read_role_response):
        # given the role exists and has a policy
        respx_mock.get("/access/api/roles/a_role_code").mock(
            side_effect=[httpx.Response(200, json=read_role_response)]
        )
        respx_mock.put("/access/api/roles/a_role_code").mock(side_effect=[httpx.Response(200, json={})])
        # and we reference a system role
        ref = access.RoleRef(id="supervisor", scope="support", code="support-iam-readonly")
        # and the desired state only a nonTransitiveSupervisor....
        ntsrs = access.NonTransitiveSupervisorRoleResource(roles=[ref])
        sut = access.RoleResource(
            id="role1",
            code="a_role_code",
            resource=access.RoleResourceRequest(non_transitive_supervisor_role_resource=ntsrs),
            when=access.WhenSpec(activate="2024-03-01:00:00.0000000+00:00"),
            permission=access.Permission.READ,
        )
        # when we update
        log = sut.update(self.client, SimpleNamespace(id="role1", code="a_role_code"))
        # then the log returned is the same
        assert log == {"code": "a_role_code", "id": "role1"}
        # and a put request to modify the role was made
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/access/api/roles/a_role_code"
        assert json.loads(request.content) == {
            "permission": "Read",  # nb no code set when its a PUT
            "resource": {
                "nonTransitiveSupervisorRoleResource": {
                    "roles": [{"scope": "support", "code": "support-iam-readonly"}]
                }
            },
            "when": {"activate": "2024-03-01:00:00.0000000+00:00"},
        }


@pytest.mark.respx(base_url=TEST_BASE)
class DescribePolicyCollectionRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_attach_when_present(self, respx_mock):
        # given that the remote definition exists
        respx_mock.get("/access/api/policycollections/cd1?scope=sc1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = access.PolicyCollectionRef(id="one", scope="sc1", code="cd1")
        # when we call attach
        sut.attach(client)
        # then a get request was made and no exception raised

    def test_attach_when_missing(self, respx_mock):
        # given the remote does not exist
        respx_mock.get("/access/api/policycollections/cd1?scope=sc1").mock(
            return_value=httpx.Response(404, json={})
        )
        client = self.client
        sut = access.PolicyCollectionRef(id="one", scope="sc1", code="cd1")
        # when we call attach an exception is raised
        with pytest.raises(RuntimeError) as ex:
            sut.attach(client)
        assert "PolicyCollection sc1/cd1 not found" in str(ex.value)

    def test_attach_when_http_error(self, respx_mock):
        # given the server returns an error
        respx_mock.get("/access/api/policycollections/cd1?scope=sc1").mock(
            return_value=httpx.Response(500, json={})
        )
        client = self.client
        sut = access.PolicyCollectionRef(id="one", scope="sc1", code="cd1")
        # when we call attach an exception is raised
        with pytest.raises(httpx.HTTPError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribePolicyCollectionResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    @pytest.fixture
    def policy1(self):
        return access.PolicyResource(
            id="policy1",
            code="a_policy1",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.IdSelector(
                    name="banjo",
                    description="whatever",
                    identifier={"scope": "w", "code": "y"},
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )

    @pytest.fixture
    def policy2(self):
        return access.PolicyResource(
            id="policy2",
            code="a_policy2",
            description="policy description",
            applications=["lusid"],
            grant=access.Grant.ALLOW,
            when=access.WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00"),
            selectors=[
                access.MatchAllSelector(
                    name="banjo",
                    description="whatever",
                    actions=[access.ActionId(scope="actscope", activity="execute", entity="Feature")],
                )
            ],
        )

    def test_create_with_policies(self, respx_mock, policy1, policy2):
        respx_mock.post("/access/api/policycollections").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-code"}})
        )
        client = self.client
        # given a desired collection
        sut = access.PolicyCollectionResource(
            id="polly-collection", code="col-code", policies=[policy1, policy2]
        )
        # when we create it
        state = sut.create(client)
        # then the state is returned
        assert state == {"scope": "default", "code": "col-code"}
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/policycollections"
        assert json.loads(request.content) == {
            "code": "col-code",
            "policies": [
                {"scope": "default", "code": "a_policy1"},
                {"scope": "default", "code": "a_policy2"},
            ],
            "policyCollections": [],
        }

    def test_create_with_policy_ref(self, respx_mock, policy1, policy2):
        respx_mock.post("/access/api/policycollections").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-code"}})
        )
        client = self.client
        # given a policy ref to a non-default scope (eg a ref to a builtin
        # policy like an admin one
        ref = access.PolicyRef(id="ref", scope="sc1", code="cd1")
        # given a desired collection
        sut = access.PolicyCollectionResource(id="polly-collection", code="col-code", policies=[ref])
        # when we create it
        state = sut.create(client)
        # then the state is returned
        assert state == {"scope": "default", "code": "col-code"}
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/policycollections"
        assert json.loads(request.content) == {
            "code": "col-code",
            "policies": [{"scope": "sc1", "code": "cd1"}],
            "policyCollections": [],
        }

    def test_create_with_nested_collection(self, respx_mock, policy1, policy2):
        respx_mock.post("/access/api/policycollections").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-inner"}})
        )
        respx_mock.post("/access/api/policycollections").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-code"}})
        )
        client = self.client
        # given an inner collection which has already been created
        inner = access.PolicyCollectionResource(
            id="polly-collection", code="col-inner", policies=[policy1, policy2]
        )
        inner.create(self.client)
        # and a desired collection which references it
        sut = access.PolicyCollectionResource(
            id="polly-collection", code="col-code", policy_collections=[inner]
        )
        # when we create it
        state = sut.create(client)
        # then the state is returned
        assert state == {"scope": "default", "code": "col-code"}
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/access/api/policycollections"
        assert json.loads(request.content) == {
            "code": "col-code",
            "policyCollections": [{"scope": "default", "code": "col-inner"}],
            "policies": [],
        }

    def test_update_no_change(self, respx_mock, policy1, policy2):
        # given an existing collection
        respx_mock.get("/access/api/policycollections/col-code").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"code": "col-code", "scope": "default"},
                    "policies": [
                        {"scope": "default", "code": "a_policy1"},
                        {"scope": "default", "code": "a_policy2"},
                    ],
                    "policyCollections": [],
                    "links": [],
                },
            )
        )
        old_state = SimpleNamespace(scope="default", code="col-code")
        # given a desired collection
        sut = access.PolicyCollectionResource(
            id="polly-collection", code="col-code", policies=[policy1, policy2]
        )
        # when we update
        state = sut.update(self.client, old_state)
        # then state is None and no further requests are made
        assert state is None

    def test_update_rename(self, respx_mock, policy1, policy2):
        respx_mock.delete("/access/api/policycollections/col-code").mock(
            side_effect=[httpx.Response(200, json={})]
        )
        respx_mock.post("/access/api/policycollections").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-code2"}})
        )
        # given an existing collection at col-code
        old_state = SimpleNamespace(scope="default", code="col-code")
        # and a desired collection with code col-code2
        sut = access.PolicyCollectionResource(
            id="polly-collection", code="col-code2", policies=[policy1, policy2]
        )
        # when we update
        state = sut.update(self.client, old_state)
        # the new state is returned
        assert state == {"scope": "default", "code": "col-code2"}
        # and a delete and a create call were made

    def test_update_remove_policy(self, respx_mock, policy1, policy2):
        # given an existing collection
        respx_mock.get("/access/api/policycollections/col-code").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"code": "col-code", "scope": "default"},
                    "policies": [
                        {"scope": "default", "code": "a_policy1"},
                        {"scope": "default", "code": "a_policy2"},
                    ],
                    "policyCollections": [],
                    "links": [],
                },
            )
        )
        respx_mock.put("/access/api/policycollections/col-code").mock(
            return_value=httpx.Response(200, json={"id": {"scope": "default", "code": "col-code"}})
        )
        old_state = SimpleNamespace(scope="default", code="col-code")
        # given a desired collection
        sut = access.PolicyCollectionResource(id="polly-collection", code="col-code", policies=[policy1])
        # when we update
        state = sut.update(self.client, old_state)
        # then state returned
        assert state == {"scope": "default", "code": "col-code"}
        # and a put request was sent
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/access/api/policycollections/col-code"
        assert json.loads(request.content) == {
            "policies": [{"scope": "default", "code": "a_policy1"}],
            "policyCollections": [],
        }

    def test_delete(self, respx_mock):
        respx_mock.delete("/access/api/policycollections/col-code").mock(
            side_effect=[httpx.Response(200, json={})]
        )
        # given an existing collection
        # when we delete it
        old_state = SimpleNamespace(scope="default", code="col-code")
        access.PolicyCollectionResource.delete(self.client, old_state)
        # then a delete request is made
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/access/api/policycollections/col-code"

    def test_deps_policy_ref(self, respx_mock, policy1, policy2):
        ref = access.PolicyRef(id="ref", scope="sc1", code="cd1")
        # given a desired collection with two policies
        sut = access.PolicyCollectionResource(id="polly-collection", code="col-code", policies=[ref])
        # when we get the deps
        deps = sut.deps()
        assert deps == [ref]

    def test_deps_policies_only(self, respx_mock, policy1, policy2):
        # given a desired collection with two policies
        sut = access.PolicyCollectionResource(
            id="polly-collection", code="col-code", policies=[policy1, policy2]
        )
        # when we get the deps
        deps = sut.deps()
        assert deps == [policy1, policy2]

    def test_deps_collections_only(self, respx_mock, policy1, policy2):
        # given an inner collection which has already been created
        inner = access.PolicyCollectionResource(
            id="polly-collection", code="col-inner", policies=[policy1, policy2]
        )
        # and a desired collection which references it
        sut = access.PolicyCollectionResource(
            id="polly-collection", code="col-code", policy_collections=[inner]
        )
        # when we get the deps
        deps = sut.deps()
        assert deps == [inner]
