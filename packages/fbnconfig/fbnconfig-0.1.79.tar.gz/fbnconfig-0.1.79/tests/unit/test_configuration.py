import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import configuration

TEST_BASE = "https://foo.lusid.com"


def response_hook(response: httpx.Response):
    response.read()
    response.raise_for_status()


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeSetRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_attach_when_exists(self, respx_mock):
        # given a set exists
        respx_mock.get("/configuration/api/sets/personal/scope1/code1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # when we attach
        sut = configuration.SetRef(
            id="abc", scope="scope1", code="code1", type=configuration.SetType.PERSONAL
        )
        sut.attach(client)
        # then all is good an no exception

    def test_attach_when_not_exists(self, respx_mock):
        # given a set exists
        respx_mock.get("/configuration/api/sets/personal/scope1/code1").mock(
            return_value=httpx.Response(404, json={})
        )
        client = self.client
        # when we attach
        sut = configuration.SetRef(
            id="abc", scope="scope1", code="code1", type=configuration.SetType.PERSONAL
        )
        # a runtime error is raised
        with pytest.raises(RuntimeError):
            sut.attach(client)

    def test_attach_when_http_error(self, respx_mock):
        # given a server which returns a 500
        respx_mock.get("/configuration/api/sets/personal/scope1/code1").mock(
            return_value=httpx.Response(500, json={})
        )
        client = self.client
        # when we attach
        sut = configuration.SetRef(
            id="abc", scope="scope1", code="code1", type=configuration.SetType.PERSONAL
        )
        with pytest.raises(httpx.HTTPStatusError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeSetResource:
    client = httpx.Client(base_url=TEST_BASE)

    def test_create(self, respx_mock):
        respx_mock.post("/configuration/api/sets").mock(return_value=httpx.Response(200, json={}))
        # given a desired set
        sut = configuration.SetResource(
            id="xyz",
            scope="scope-a",
            code="code-a",
            type=configuration.SetType.SHARED,
            description="blah",
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned
        assert state == {"scope": "scope-a", "code": "code-a", "type": "shared"}
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/configuration/api/sets"
        assert json.loads(request.content) == {
            "id": {"scope": "scope-a", "code": "code-a"},
            "type": "shared",
            "description": "blah",
        }

    def test_update_with_no_changes(self, respx_mock):
        # given an existing set
        respx_mock.get("/configuration/api/sets/personal/scope-b/code-b").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"scope": "scope-b", "code": "code-b"},
                    "type": "personal",
                    "description": "nice set!",
                    "createdAt": "2023-01-02",
                    "createdBy": "sarah",
                    "lastModifiedAt": "",
                    "lastModifiedBy": "",
                    "items": [],
                    "links": {},
                },
            )
        )
        # and a desired set
        sut = configuration.SetResource(
            id="xyz",
            scope="scope-b",
            code="code-b",
            type=configuration.SetType.PERSONAL,
            description="nice set!",
        )
        old_state = SimpleNamespace(scope="scope-b", code="code-b", type="personal")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is None
        assert state is None
        # and a read was made but no PUT

    def test_update_with_modified_description(self, respx_mock):
        # given an existing set
        respx_mock.get("/configuration/api/sets/personal/scope-b/code-b").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": {"scope": "scope-b", "code": "code-b"},
                    "type": "personal",
                    "description": "nice set!",
                    "createdAt": "2023-01-02",
                    "createdBy": "sarah",
                    "lastModifiedAt": "",
                    "lastModifiedBy": "",
                    "items": [],
                    "links": {},
                },
            )
        )
        respx_mock.put("/configuration/api/sets/personal/scope-b/code-b").mock(
            return_value=httpx.Response(200, json={})
        )
        # and a desired set
        sut = configuration.SetResource(
            id="xyz",
            scope="scope-b",
            code="code-b",
            type=configuration.SetType.PERSONAL,
            description="great party Jeff!",
        )
        old_state = SimpleNamespace(scope="scope-b", code="code-b", type="personal")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the existing state is returned
        assert state == {"scope": "scope-b", "code": "code-b", "type": "personal"}
        # and the put is sent
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/configuration/api/sets/personal/scope-b/code-b"
        assert json.loads(request.content) == {"description": "great party Jeff!"}

    def test_update_with_change_scope_should_throw(self, respx_mock):
        sut = configuration.SetResource(
            id="xyz",
            scope="new-scope",
            code="code-b",
            type=configuration.SetType.PERSONAL,
            description="great party Jeff!",
        )
        old_state = SimpleNamespace(scope="scope-b", code="code-b", type="personal")
        # when we update it throws
        with pytest.raises(RuntimeError):
            sut.update(self.client, old_state)

    def test_update_with_change_code_should_throw(self, respx_mock):
        sut = configuration.SetResource(
            id="xyz",
            scope="scope-b",
            code="new-code",
            type=configuration.SetType.PERSONAL,
            description="great party Jeff!",
        )
        old_state = SimpleNamespace(scope="scope-b", code="code-b", type="personal")
        # when we update it throws
        with pytest.raises(RuntimeError):
            sut.update(self.client, old_state)

    def test_update_with_change_type_should_throw(self, respx_mock):
        sut = configuration.SetResource(
            id="xyz",
            scope="scope-b",
            code="code-b",
            type=configuration.SetType.SHARED,
            description="great party Jeff!",
        )
        old_state = SimpleNamespace(scope="scope-b", code="code-b", type="personal")
        # when we update it throws
        with pytest.raises(RuntimeError):
            sut.update(self.client, old_state)

    def test_delete(self, respx_mock):
        respx_mock.delete("/configuration/api/sets/shared/scope-b/code-b").mock(
            return_value=httpx.Response(200, json={})
        )
        # given a set that exists in the remnte
        old_state = SimpleNamespace(scope="scope-b", code="code-b", type="shared")
        # when we delete it
        configuration.SetResource.delete(self.client, old_state)
        # then a delete request is sent with the roleId
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/configuration/api/sets/shared/scope-b/code-b"

    def test_deps(self):
        sut = configuration.SetResource(
            id="xyz",
            scope="scope-b",
            code="code-b",
            type=configuration.SetType.SHARED,
            description="great party Jeff!",
        )
        # it's deps are empty
        assert sut.deps() == []


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeItemRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    @pytest.fixture
    def existing_set(self):
        return configuration.SetRef(
            id="abc", scope="scope1", code="code1", type=configuration.SetType.PERSONAL
        )

    def test_attach_when_exists(self, respx_mock, existing_set):
        # given an item in the remote
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(200, json={"ref": "config://xyz"})
        )
        client = self.client
        # when we attach
        sut = configuration.ItemRef(id="111", set=existing_set, key="key1")
        sut.attach(client)
        # then all is good no exception and the ref is set
        assert sut.ref == "config://xyz"

    def test_attach_when_not_exists(self, respx_mock, existing_set):
        # given no matching remote
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(404, json={})
        )
        client = self.client
        # when we attach
        sut = configuration.ItemRef(id="111", set=existing_set, key="key1")
        # it throws
        with pytest.raises(RuntimeError):
            sut.attach(client)

    def test_attach_when_http_error(self, respx_mock, existing_set):
        # given a 500
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(500, json={})
        )
        client = self.client
        # when we attach
        sut = configuration.ItemRef(id="111", set=existing_set, key="key1")
        # a http error
        with pytest.raises(httpx.HTTPStatusError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeItemResource:
    client = httpx.Client(base_url=TEST_BASE)

    @pytest.fixture
    def existing_set(self):
        return configuration.SetRef(
            id="set1", scope="scope1", code="code1", type=configuration.SetType.PERSONAL
        )

    def test_create(self, respx_mock, existing_set):
        respx_mock.post("/configuration/api/sets/personal/scope1/code1/items").mock(
            return_value=httpx.Response(200, json={"items": [{"key": "key1", "ref": "config://1234"}]})
        )
        # given a desired item
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="secret-value",
            value_type=configuration.ValueType.TEXT,
            is_secret=False,
            description="something",
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned
        assert state == {"scope": "scope1", "code": "code1", "type": "personal", "key": "key1"}
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/configuration/api/sets/personal/scope1/code1/items"
        assert json.loads(request.content) == {
            "key": "key1",
            "value": "secret-value",
            "valueType": "text",
            "isSecret": False,
            "description": "something",
            "blockReveal": False,
        }
        # and the ref value has been set
        assert sut.ref == "config://1234"

    def test_update_with_no_change(self, respx_mock, existing_set):
        # given a matching item aready exists in the remote
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "key": "key1",
                    "value": "secret-value",
                    "valueType": "text",
                    "isSecret": False,
                    "description": "something",
                    "blockReveal": False,
                    "createdAt": "2023-01-02",
                    "createdBy": "sarah",
                    "lastModifiedAt": "",
                    "lastModifiedBy": "",
                    "ref": "config/123",
                },
            )
        )
        # and a desired item which matches the remote
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="secret-value",
            value_type=configuration.ValueType.TEXT,
            is_secret=False,
            description="something",
        )
        old_state = SimpleNamespace(scope="scope1", code="code1", type="personal", key="key1")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is None
        assert state is None
        # and no put request was made
        # and the ref value has been set
        assert sut.ref == "config/123"

    def test_update_with_modified_valuetype(self, respx_mock, existing_set):
        # given an item already exists in the remote with a value of false
        # but valueType of text
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "key": "key1",
                    "value": "secret-value",
                    "valueType": "text",
                    "isSecret": False,
                    "description": "something",
                    "blockReveal": False,
                    "createdAt": "2023-01-02",
                    "createdBy": "sarah",
                    "lastModifiedAt": "",
                    "lastModifiedBy": "",
                    "ref": "config/123",
                },
            )
        )
        respx_mock.post("/configuration/api/sets/personal/scope1/code1/items").mock(
            return_value=httpx.Response(200, json={"items": [{"key": "key1", "ref": "config://1234"}]})
        )
        respx_mock.delete("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(200, json={"ref": "config/123"})
        )
        # and a desired item which changes the value type to boolean
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="false",
            value_type=configuration.ValueType.BOOLEAN,
            is_secret=False,
            description="something new",
        )
        old_state = SimpleNamespace(scope="scope1", code="code1", type="personal", key="key1")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the existing state is returned
        assert state == {"scope": "scope1", "code": "code1", "type": "personal", "key": "key1"}
        # and a delete and post are done to recreate with a different valuetype
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/configuration/api/sets/personal/scope1/code1/items"
        assert json.loads(request.content) == {
            "valueType": "boolean",
            "value": "false",
            "description": "something new",
            "blockReveal": False,
            "isSecret": False,
            "key": "key1",
        }

    def test_update_with_modified_description(self, respx_mock, existing_set):
        # given a matching item already exists in the remote
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "key": "key1",
                    "value": "secret-value",
                    "valueType": "text",
                    "isSecret": False,
                    "description": "something",
                    "blockReveal": False,
                    "createdAt": "2023-01-02",
                    "createdBy": "sarah",
                    "lastModifiedAt": "",
                    "lastModifiedBy": "",
                    "ref": "config/123",
                },
            )
        )
        respx_mock.put("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(200, json={"ref": "config/123"})
        )
        # and a desired item which matches the remote
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="secret-value",
            value_type=configuration.ValueType.TEXT,
            is_secret=False,
            description="something new",
        )
        old_state = SimpleNamespace(scope="scope1", code="code1", type="personal", key="key1")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the existing state is returned
        assert state == {"scope": "scope1", "code": "code1", "type": "personal", "key": "key1"}
        # and the put is sent
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/configuration/api/sets/personal/scope1/code1/items/key1"
        assert json.loads(request.content) == {
            "value": "secret-value",
            "description": "something new",
            "blockReveal": False,
        }

    def test_update_with_modified_block_reveal(self, respx_mock, existing_set):
        # given a matching item already exists in the remote
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "key": "key1",
                    "value": "secret-value",
                    "valueType": "text",
                    "isSecret": False,
                    "description": "something",
                    "blockReveal": False,
                    "createdAt": "2023-01-02",
                    "createdBy": "sarah",
                    "lastModifiedAt": "",
                    "lastModifiedBy": "",
                    "ref": "config/123",
                },
            )
        )
        respx_mock.put("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(200, json={"ref": "config/123"})
        )
        # and a desired item which matches the remote
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="secret-value",
            value_type=configuration.ValueType.TEXT,
            is_secret=False,
            description="something new",
            block_reveal=True,
        )
        old_state = SimpleNamespace(scope="scope1", code="code1", type="personal", key="key1")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the existing state is returned
        assert state == {"scope": "scope1", "code": "code1", "type": "personal", "key": "key1"}
        # and the put is sent
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert request.url.path == "/configuration/api/sets/personal/scope1/code1/items/key1"
        assert json.loads(request.content) == {
            "value": "secret-value",
            "description": "something new",
            "blockReveal": True,
        }

    def test_update_with_modified_location_recreates(self, respx_mock, existing_set):
        respx_mock.post("/configuration/api/sets/personal/scope1/code1/items").mock(
            return_value=httpx.Response(200, json={"items": [{"key": "key1", "ref": "config://1234"}]})
        )
        respx_mock.delete("/configuration/api/sets/personal/scope1/oldcode/items/key1").mock(
            return_value=httpx.Response(200, json={"ref": "config/123"})
        )
        # and a desired item which matches the remote
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="secret-value",
            value_type=configuration.ValueType.TEXT,
            is_secret=False,
            description="something new",
        )
        old_state = SimpleNamespace(scope="scope1", code="oldcode", type="personal", key="key1")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the existing state is returned
        assert state == {"scope": "scope1", "code": "code1", "type": "personal", "key": "key1"}
        # a delete and a post are made

    def test_update_with_modified_details_recreates(self, respx_mock, existing_set):
        # given an existing item which is secret
        respx_mock.get("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "key": "key1",
                    "value": "secret-value",
                    "valueType": "text",
                    "isSecret": True,
                    "description": "something",
                    "createdAt": "2023-01-02",
                    "createdBy": "sarah",
                    "lastModifiedAt": "",
                    "lastModifiedBy": "",
                    "ref": "config/123",
                },
            )
        )
        respx_mock.post("/configuration/api/sets/personal/scope1/code1/items").mock(
            return_value=httpx.Response(200, json={"items": [{"key": "key1", "ref": "config://1234"}]})
        )
        respx_mock.delete("/configuration/api/sets/personal/scope1/code1/items/key1").mock(
            return_value=httpx.Response(200, json={"ref": "config/123"})
        )
        # and a desired item which is not
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="secret-value",
            value_type=configuration.ValueType.TEXT,
            is_secret=False,
            description="something new",
        )
        old_state = SimpleNamespace(scope="scope1", code="code1", type="personal", key="key1")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the existing state is returned
        assert state == {"scope": "scope1", "code": "code1", "type": "personal", "key": "key1"}
        # a delete and a post are made

    def test_delete(self, respx_mock):
        respx_mock.delete("/configuration/api/sets/shared/scope-b/code-b/items/key1").mock(
            return_value=httpx.Response(200, json={})
        )
        # given a set that exists in the remnte
        old_state = SimpleNamespace(scope="scope-b", code="code-b", type="shared", key="key1")
        # when we delete it
        configuration.ItemResource.delete(self.client, old_state)
        # then a delete request is sent with the roleId
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/configuration/api/sets/shared/scope-b/code-b/items/key1"

    @staticmethod
    def test_deps(existing_set):
        # and a desired item which matches the remote
        sut = configuration.ItemResource(
            id="xyz",
            set=existing_set,
            key="key1",
            value="secret-value",
            value_type=configuration.ValueType.TEXT,
            is_secret=False,
            description="something new",
        )
        # it depends on the set
        assert sut.deps() == [existing_set]


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeSystemConfig:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_create_given_config_does_not_exist_then_fail(self, respx_mock):
        (
            respx_mock.put("/configuration/api/sets/shared/system/somecode/items/shouldnotexist").mock(
                return_value=httpx.Response(
                    404,
                    json={
                        "name": "ConfigurationNotFound",
                        "code": 710,
                        "title": "Configuration item not found",
                        "detail": "Server message for not found",
                        "status": 404,
                    },
                )
            )
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="somecode",
            key="shouldnotexist",
            value="whatever",
            description="something",
            default_value="something",
        )

        from httpx import HTTPStatusError

        with pytest.raises(HTTPStatusError) as ex:
            sut.create(self.client)
        request = respx_mock.calls.last.request
        assert request.method == "PUT"
        assert "404 Not Found" in ex.exconly(tryshort=True)

    def test_create_given_config_exists_then_updates(self, respx_mock):
        respx_mock.put(
            "/configuration/api/sets/shared/system/TransactionBooking/items/ValidateInstruments"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "key": "ValidateInstruments",
                    "value": "False",
                    "valueType": "boolean",
                    "ref": "config://shared/system/TransactionBooking/ValidateInstruments",
                },
            )
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="TransactionBooking",
            key="ValidateInstruments",
            value="False",
            description="something",
            default_value=None,
        )

        state = sut.create(self.client)
        assert state == {
            "code": "TransactionBooking",
            "key": "ValidateInstruments",
            "default_value": None,
        }

    def test_read_given_config_exists(self, respx_mock):
        (
            respx_mock.get(
                "/configuration/api/sets/system/TransactionBooking/items/ValidateInstruments"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "values": [
                            {
                                "key": "ValidateInstruments",
                                "value": "True",
                                "valueType": "boolean",
                                "isSecret": "false",
                                "ref": "config://shared/system/TransactionBooking/ValidateInstruments",
                            }
                        ]
                    },
                )
            )
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="TransactionBooking",
            key="ValidateInstruments",
            value="False",
            description="something",
            default_value="something",
        )
        old_state = {"code": "TransactionBooking", "key": "ValidateInstruments"}
        sut.read(self.client, SimpleNamespace(**old_state))

    def test_update_given_no_change_then_no_calls(self, respx_mock):
        (
            respx_mock.get(
                "/configuration/api/sets/system/TransactionBooking/items/ValidateInstruments"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "values": [
                            {
                                "key": "ValidateInstruments",
                                "value": "True",
                                "valueType": "boolean",
                                "isSecret": "false",
                                "ref": "config://shared/system/TransactionBooking/ValidateInstruments",
                                "description": "something",
                                "blockReveal": False,
                            }
                        ]
                    },
                )
            )
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="TransactionBooking",
            key="ValidateInstruments",
            value="True",
            description="something",
            default_value="something",
        )

        old_state = {"code": "TransactionBooking", "key": "ValidateInstruments"}
        state = sut.update(self.client, SimpleNamespace(**old_state))
        assert state is None

    def test_update_given_value_and_description_change(self, respx_mock):
        (
            respx_mock.get(
                "/configuration/api/sets/system/TransactionBooking/items/ValidateInstruments"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "values": [
                            {
                                "key": "ValidateInstruments",
                                "value": "True",
                                "valueType": "boolean",
                                "isSecret": "false",
                                "ref": "config://shared/system/TransactionBooking/ValidateInstruments",
                                "description": "something else",
                                "blockReveal": False,
                            }
                        ]
                    },
                )
            )
        )

        (
            respx_mock.put(
                "/configuration/api/sets/shared/system/TransactionBooking/items/ValidateInstruments"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "key": "ValidateInstruments",
                        "value": "False",
                        "valueType": "boolean",
                        "ref": "config://shared/system/TransactionBooking/ValidateInstruments",
                        "description": "something else",
                        "blockReveal": False,
                    },
                )
            )
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="TransactionBooking",
            key="ValidateInstruments",
            value="False",
            description="something",
            default_value=None,
            block_reveal=True,
        )

        old_state = {"code": "TransactionBooking", "key": "ValidateInstruments", "default_value": None}
        state = sut.update(self.client, SimpleNamespace(**old_state))
        assert state == old_state
        request = respx_mock.calls.last.request
        assert json.loads(request.content) == {
            "value": "False",
            "description": "something",
            "blockReveal": True,
        }

    def test_update_with_modified_key_deletes_and_recreates(self, respx_mock):
        (
            respx_mock.put(
                "/configuration/api/sets/shared/system/TransactionBooking/items/ValidateInstruments"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "key": "ValidateInstruments",
                        "value": "False",
                        "valueType": "boolean",
                        "ref": "config://shared/system/TransactionBooking/ValidateInstruments",
                        "description": "something else",
                    },
                )
            )
        )

        (
            respx_mock.put(
                "/configuration/api/sets/shared/system/TransactionBooking/items/SomeOtherKey"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "key": "SomeOtherKey",
                        "value": "True",
                        "valueType": "boolean",
                        "ref": "config://shared/system/TransactionBooking/SomeOtherKey",
                        "description": "something",
                    },
                )
            )
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="TransactionBooking",
            key="SomeOtherKey",
            value="True",
            description="something",
            default_value=None,
        )

        old_state = {
            "scope": "system",
            "code": "TransactionBooking",
            "type": "shared",
            "key": "ValidateInstruments",
            "default_value": "False",
        }

        state = sut.update(self.client, SimpleNamespace(**old_state))
        assert state is not None
        assert state["key"] == "SomeOtherKey"
        assert state["code"] == "TransactionBooking"

    def test_update_with_modified_code_deletes_and_recreates(self, respx_mock):
        (
            respx_mock.put(
                "/configuration/api/sets/shared/system/TransactionBooking/items/ValidateInstruments"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "key": "ValidateInstruments",
                        "value": "False",
                        "valueType": "boolean",
                        "ref": "config://shared/system/TransactionBooking/ValidateInstruments",
                        "description": "something else",
                    },
                )
            )
        )

        (
            respx_mock.put(
                "/configuration/api/sets/shared/system/SomeOtherCode/items/ValidateInstruments"
            ).mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "key": "ValidateInstruments",
                        "value": "True",
                        "valueType": "boolean",
                        "ref": "config://shared/system/SomeOtherCode/SomeOtherKey",
                        "description": "something",
                    },
                )
            )
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="SomeOtherCode",
            key="ValidateInstruments",
            value="True",
            description="something",
            default_value=None,
        )

        old_state = {
            "code": "TransactionBooking",
            "key": "ValidateInstruments",
            "default_value": "False",
        }

        state = sut.update(self.client, SimpleNamespace(**old_state))
        assert state is not None
        assert state["key"] == "ValidateInstruments"
        assert state["code"] == "SomeOtherCode"

    def test_delete(self):
        sut = configuration.SystemConfigResource(
            id="pass",
            code="TransactionBooking",
            key="Something",
            value="False",
            description="some",
            default_value=None,
        )
        # nothing should happen
        sut.delete(self.client, SimpleNamespace(**{"default_value": None}))

    @staticmethod
    def test_deps():
        sut = configuration.SystemConfigResource(
            id="pass",
            code="somecode",
            key="Something",
            value="False",
            description="some",
            default_value=None,
        )
        assert sut.deps() == []

    def test_delete_given_default_value_then_updates(self, respx_mock):
        (
            respx_mock.put(
                "/configuration/api/sets/shared/system/TransactionBooking/items/ValidateInstruments"
            ).mock(return_value=httpx.Response(200, json={"something": "something"}))
        )

        sut = configuration.SystemConfigResource(
            id="txnbooking",
            code="TransactionBooking",
            key="ValidateInstruments",
            value="True",
            description="something",
            default_value="False",
        )
        old_state = {
            "code": "TransactionBooking",
            "key": "ValidateInstruments",
            "default_value": "False",
        }
        sut.delete(self.client, SimpleNamespace(**old_state))

        request = respx_mock.calls.last.request
        assert json.loads(request.content) == {"value": "False"}
