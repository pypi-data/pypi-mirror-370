import json

import httpx
import pytest

from fbnconfig import datatype as dt
from fbnconfig import property as prop
from fbnconfig import reference_list as rl

TEST_BASE = "https://foo.lusid.com"


def response_hook(response: httpx.Response):
    response.read()
    response.raise_for_status()


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeReferenceListResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [response_hook]})

    def test_create(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a desired reference list with a string list
        sut = rl.ReferenceListResource(
            id="ref1",
            scope="scope-a",
            code="code-a",
            name="Test Reference List",
            description="A test reference list",
            tags=["test", "example"],
            reference_list=rl.StringList(values=["value1", "value2", "value3"])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-a"
        assert state["code"] == "code-a"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-a", "code": "code-a"}
        assert request_body["name"] == "Test Reference List"
        assert request_body["description"] == "A test reference list"
        assert request_body["tags"] == ["test", "example"]
        assert request_body["referenceList"]["values"] == ["value1", "value2", "value3"]
        assert request_body["referenceList"]["referenceListType"] == "StringList"

    def test_create_with_portfolio_group_id_list(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a desired reference list with a portfolio group id list
        sut = rl.ReferenceListResource(
            id="ref2",
            scope="scope-b",
            code="code-b",
            name="Portfolio Group Reference List",
            reference_list=rl.PortfolioGroupIdList(values=[
                rl.ResourceId(scope="group-scope", code="group-1"),
                rl.ResourceId(scope="group-scope", code="group-2")
            ])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-b"
        assert state["code"] == "code-b"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-b", "code": "code-b"}
        assert request_body["name"] == "Portfolio Group Reference List"
        assert request_body["referenceList"]["values"] == [
            {"scope": "group-scope", "code": "group-1"},
            {"scope": "group-scope", "code": "group-2"}
        ]
        assert request_body["referenceList"]["referenceListType"] == "PortfolioGroupIdList"

    def test_create_with_portfolio_id_list(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a desired reference list with a portfolio id list
        sut = rl.ReferenceListResource(
            id="ref3",
            scope="scope-c",
            code="code-c",
            name="Portfolio Reference List",
            reference_list=rl.PortfolioIdList(values=[
                rl.ResourceId(scope="portfolio-scope", code="portfolio-1"),
                rl.ResourceId(scope="portfolio-scope", code="portfolio-2")
            ])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-c"
        assert state["code"] == "code-c"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-c", "code": "code-c"}
        assert request_body["name"] == "Portfolio Reference List"
        assert request_body["referenceList"]["values"] == [
            {"scope": "portfolio-scope", "code": "portfolio-1"},
            {"scope": "portfolio-scope", "code": "portfolio-2"}
        ]
        assert request_body["referenceList"]["referenceListType"] == "PortfolioIdList"

    def test_create_with_decimal_list(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a desired reference list with a decimal list
        sut = rl.ReferenceListResource(
            id="ref4",
            scope="scope-d",
            code="code-d",
            name="Decimal Reference List",
            reference_list=rl.DecimalList(values=[1.5, 2.75, 3.0, 4.25])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-d"
        assert state["code"] == "code-d"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-d", "code": "code-d"}
        assert request_body["name"] == "Decimal Reference List"
        assert request_body["referenceList"]["values"] == [1.5, 2.75, 3.0, 4.25]
        assert request_body["referenceList"]["referenceListType"] == "DecimalList"

    def test_create_with_fund_id_list(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a desired reference list with a fund id list
        sut = rl.ReferenceListResource(
            id="ref5",
            scope="scope-e",
            code="code-e",
            name="Fund Reference List",
            reference_list=rl.FundIdList(values=[
                rl.ResourceId(scope="fund-scope", code="fund-1"),
                rl.ResourceId(scope="fund-scope", code="fund-2")
            ])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-e"
        assert state["code"] == "code-e"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-e", "code": "code-e"}
        assert request_body["name"] == "Fund Reference List"
        assert request_body["referenceList"]["values"] == [
            {"scope": "fund-scope", "code": "fund-1"},
            {"scope": "fund-scope", "code": "fund-2"}
        ]
        assert request_body["referenceList"]["referenceListType"] == "FundIdList"

    def test_create_with_address_key_list(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a desired reference list with an address key list
        sut = rl.ReferenceListResource(
            id="ref6",
            scope="scope-f",
            code="code-f",
            name="Address Key Reference List",
            reference_list=rl.AddressKeyList(values=["address-key-1", "address-key-2", "address-key-3"])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-f"
        assert state["code"] == "code-f"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-f", "code": "code-f"}
        assert request_body["name"] == "Address Key Reference List"
        assert request_body["referenceList"]["values"] == [
            "address-key-1", "address-key-2", "address-key-3"
        ]
        assert request_body["referenceList"]["referenceListType"] == "AddressKeyList"

    def test_create_with_instrument_list(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a desired reference list with an instrument list
        sut = rl.ReferenceListResource(
            id="ref7",
            scope="scope-g",
            code="code-g",
            name="Instrument Reference List",
            reference_list=rl.InstrumentList(values=["LUID_12345", "LUID_67890", "LUID_11111"])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-g"
        assert state["code"] == "code-g"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-g", "code": "code-g"}
        assert request_body["name"] == "Instrument Reference List"
        assert request_body["referenceList"]["values"] == ["LUID_12345", "LUID_67890", "LUID_11111"]
        assert request_body["referenceList"]["referenceListType"] == "InstrumentList"

    def test_create_with_property_list(self, respx_mock):
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given property definitions for the property list
        prop_def = prop.DefinitionResource(
            id="test-prop",
            domain=prop.Domain.Portfolio,
            scope="test-scope",
            code="test-property",
            display_name="Test Property",
            data_type_id=dt.DataTypeRef(id="string-dt", scope="system", code="string"),
            property_description="A test property for reference lists"
        )
        # given a desired reference list with a property list
        sut = rl.ReferenceListResource(
            id="ref8",
            scope="scope-h",
            code="code-h",
            name="Property Reference List",
            reference_list=rl.PropertyList(values=[
                rl.PropertyListItem(
                    property_definition=prop_def,
                    label_value="test-label-1",
                    metric_value=None,
                    label_set_value=None
                ),
                rl.PropertyListItem(
                    property_definition=prop_def,
                    label_value="test-label-2",
                    metric_value=None,
                    label_set_value=None
                )
            ])
        )
        # when we create it
        state = sut.create(self.client)
        # then the state is returned with content hash
        assert state["scope"] == "scope-h"
        assert state["code"] == "code-h"
        assert "content_hash" in state
        # and a create request was sent
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-h", "code": "code-h"}
        assert request_body["name"] == "Property Reference List"
        assert len(request_body["referenceList"]["values"]) == 2
        # Check the first property list item
        first_item = request_body["referenceList"]["values"][0]
        assert first_item["key"] == "Portfolio/test-scope/test-property"
        assert first_item["labelValue"] == "test-label-1"
        assert "metricValue" not in first_item
        assert "labelSetValue" not in first_item
        # Check the second property list item
        second_item = request_body["referenceList"]["values"][1]
        assert second_item["key"] == "Portfolio/test-scope/test-property"
        assert second_item["labelValue"] == "test-label-2"
        assert "metricValue" not in second_item
        assert "labelSetValue" not in second_item

    def test_deps_with_string_list(self):
        # given a reference list with a string list
        sut = rl.ReferenceListResource(
            id="ref1",
            scope="scope-a",
            code="code-a",
            name="Test Reference List",
            reference_list=rl.StringList(values=["value1", "value2", "value3"])
        )
        # when we get its dependencies
        deps = sut.deps()
        # then it has no dependencies
        assert deps == []

    def test_deps_with_property_list(self):
        # given property definitions for the property list
        prop_def1 = prop.DefinitionResource(
            id="test-prop1",
            domain=prop.Domain.Portfolio,
            scope="test-scope",
            code="test-property-1",
            display_name="Test Property 1",
            data_type_id=dt.DataTypeRef(id="string-dt", scope="system", code="string"),
            property_description="First test property"
        )
        prop_def2 = prop.DefinitionRef(
            id="test-prop2",
            domain=prop.Domain.Portfolio,
            scope="test-scope",
            code="test-property-2",
        )
        # given a reference list with a property list using multiple property definitions
        sut = rl.ReferenceListResource(
            id="ref8",
            scope="scope-h",
            code="code-h",
            name="Property Reference List",
            reference_list=rl.PropertyList(values=[
                rl.PropertyListItem(
                    property_definition=prop_def1,
                    label_value="test-label-1",
                    metric_value=None,
                    label_set_value=None
                ),
                rl.PropertyListItem(
                    property_definition=prop_def2,
                    label_value="test-label-2",
                    metric_value=None,
                    label_set_value=None
                )
            ])
        )
        # when we get its dependencies
        deps = sut.deps()
        # then it should return both property definitions
        assert len(deps) == 2
        assert prop_def1 in deps
        assert prop_def2 in deps

    def test_deps_with_property_list_duplicate_properties(self):
        # given a property definition that will be used multiple times
        prop_def = prop.DefinitionResource(
            id="test-prop",
            domain=prop.Domain.Portfolio,
            scope="test-scope",
            code="test-property",
            display_name="Test Property",
            data_type_id=dt.DataTypeRef(id="string-dt", scope="system", code="string"),
            property_description="A test property"
        )
        # given a reference list with a property list using the same property definition multiple times
        sut = rl.ReferenceListResource(
            id="ref8",
            scope="scope-h",
            code="code-h",
            name="Property Reference List",
            reference_list=rl.PropertyList(values=[
                rl.PropertyListItem(
                    property_definition=prop_def,
                    label_value="test-label-1",
                    metric_value=None,
                    label_set_value=None
                ),
                rl.PropertyListItem(
                    property_definition=prop_def,
                    label_value="test-label-2",
                    metric_value=None,
                    label_set_value=None
                ),
                rl.PropertyListItem(
                    property_definition=prop_def,
                    label_value="test-label-3",
                    metric_value=None,
                    label_set_value=None
                )
            ])
        )
        # when we get its dependencies
        deps = sut.deps()
        # then it should return the property definition only once (deduplicated)
        assert len(deps) == 1
        assert deps[0] == prop_def

    def test_update_with_no_changes(self, respx_mock):
        from types import SimpleNamespace
        # given a reference list with a string list
        sut = rl.ReferenceListResource(
            id="ref1",
            scope="scope-a",
            code="code-a",
            name="Test Reference List",
            description="A test reference list",
            tags=["test", "example"],
            reference_list=rl.StringList(values=["value1", "value2", "value3"])
        )
        # and an old state with the same content hash
        desired = sut.model_dump(mode="json", exclude_none=True, by_alias=True)
        sorted_desired = json.dumps(desired, sort_keys=True)
        from hashlib import sha256
        content_hash = sha256(sorted_desired.encode()).hexdigest()
        old_state = SimpleNamespace(scope="scope-a", code="code-a", content_hash=content_hash)
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is None (no changes needed)
        assert state is None
        # and no HTTP requests were made
        assert len(respx_mock.calls) == 0

    def test_update_with_changes(self, respx_mock):
        from types import SimpleNamespace
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a reference list with a string list
        sut = rl.ReferenceListResource(
            id="ref1",
            scope="scope-a",
            code="code-a",
            name="Test Reference List",
            description="A test reference list",
            tags=["test", "example"],
            reference_list=rl.StringList(values=["value1", "value2", "value3"])
        )
        # and an old state with a different content hash
        old_state = SimpleNamespace(scope="scope-a", code="code-a", content_hash="different_hash")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the state is returned with new content hash
        assert state is not None
        assert state["scope"] == "scope-a"
        assert state["code"] == "code-a"
        assert "content_hash" in state
        assert state["content_hash"] != "different_hash"
        # and a POST request was made to update the reference list
        request = respx_mock.calls.last.request
        assert request.method == "POST"
        assert request.url.path == "/api/api/referencelists"
        request_body = json.loads(request.content)
        assert request_body["id"] == {"scope": "scope-a", "code": "code-a"}
        assert request_body["name"] == "Test Reference List"

    def test_update_with_scope_code_change(self, respx_mock):
        from types import SimpleNamespace
        respx_mock.delete("/api/api/referencelists/old-scope/old-code").mock(
            return_value=httpx.Response(200, json={})
        )
        respx_mock.post("/api/api/referencelists").mock(return_value=httpx.Response(200, json={}))
        # given a reference list with new scope/code
        sut = rl.ReferenceListResource(
            id="ref1",
            scope="new-scope",
            code="new-code",
            name="Test Reference List",
            reference_list=rl.StringList(values=["value1", "value2", "value3"])
        )
        # and an old state with different scope/code
        old_state = SimpleNamespace(scope="old-scope", code="old-code", content_hash="old_hash")
        # when we update it
        state = sut.update(self.client, old_state)
        # then the old one is deleted and a new one is created
        assert state is not None
        assert state["scope"] == "new-scope"
        assert state["code"] == "new-code"
        assert "content_hash" in state
        # and both DELETE and POST requests were made
        assert len(respx_mock.calls) == 2
        delete_request = respx_mock.calls[0].request
        assert delete_request.method == "DELETE"
        assert delete_request.url.path == "/api/api/referencelists/old-scope/old-code"
        create_request = respx_mock.calls[1].request
        assert create_request.method == "POST"
        assert create_request.url.path == "/api/api/referencelists"

    def test_delete(self, respx_mock):
        from types import SimpleNamespace
        respx_mock.delete("/api/api/referencelists/scope-a/code-a").mock(
            return_value=httpx.Response(200, json={})
        )
        # given a resource that exists in the remote
        old_state = SimpleNamespace(scope="scope-a", code="code-a")
        # when we delete it
        rl.ReferenceListResource.delete(self.client, old_state)
        # then a DELETE request was made
        request = respx_mock.calls.last.request
        assert request.method == "DELETE"
        assert request.url.path == "/api/api/referencelists/scope-a/code-a"

    def test_create_property_list_with_both_metric_and_label_values_throws(self):
        # given property definitions for the property list
        prop_def = prop.DefinitionResource(
            id="test-prop",
            domain=prop.Domain.Portfolio,
            scope="test-scope",
            code="test-property",
            display_name="Test Property",
            data_type_id=dt.DataTypeRef(id="string-dt", scope="system", code="string"),
            property_description="A test property for reference lists"
        )
        # when we try to create a PropertyListItem with both metric_value and label_value set
        with pytest.raises(KeyError, match="Cannot set label_value and metric_value"):
            rl.PropertyListItem(
                property_definition=prop_def,
                label_value="test-label",
                metric_value=rl.MetricValue(value=123.45, unit="USD"),
                label_set_value=None
            )
