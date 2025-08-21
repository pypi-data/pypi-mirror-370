import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import datatype, property

TEST_BASE = "https://foo.lusid.com"


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeDefinitionRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [lambda x: x.raise_for_status()]})

    def test_attach_when_present(self, respx_mock):
        # given that the remote definition exists
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = property.DefinitionRef(id="one", domain=property.Domain.Holding, scope="sc1", code="cd1")
        # when we call attach
        sut.attach(client)
        # then a get request was made and no exception raised

    def test_attach_when_missing(self, respx_mock):
        # given the remote does not exist
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(404, json={})
        )
        client = self.client
        sut = property.DefinitionRef(id="one", domain=property.Domain.Holding, scope="sc1", code="cd1")
        # when we call attach an exception is raised
        with pytest.raises(RuntimeError) as ex:
            sut.attach(client)
        assert "Property definition Holding/sc1/cd" in str(ex.value)

    def test_attach_when_http_error(self, respx_mock):
        # given the server returns an error
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(400, json={})
        )
        client = self.client
        sut = property.DefinitionRef(id="one", domain=property.Domain.Holding, scope="sc1", code="cd1")
        # when we call attach an exception is raised
        with pytest.raises(httpx.HTTPError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeDefinitionResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [lambda x: x.raise_for_status()]})

    @pytest.fixture
    def property_refs(self):
        names = ["x", "y"]
        domain = property.Domain.Instrument
        return [
            property.DefinitionRef(id=name, domain=domain, scope="refs", code=name) for name in names
        ]

    def test_create_value_prop(self, respx_mock):
        respx_mock.post("/api/api/propertydefinitions").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            life_time=property.LifeTime.Perpetual,
            constraint_style=property.ConstraintStyle.Property,
        )
        # when we call create
        state = sut.create(client)
        # then a post is made with the expected fields
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
            "propertyDescription": "description",
            "lifeTime": "Perpetual",
            "constraintStyle": "Property",
        }
        assert state == {"scope": "sc1", "code": "cd1", "domain": "Holding", "derived": False}

    def test_create_value_prop_optional_fields(self, respx_mock):
        respx_mock.post("/api/api/propertydefinitions").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
        )
        # when we call create
        sut.create(client)
        # then a post is made with the expected fields
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
        }

    def test_create_derived_prop(self, respx_mock, property_refs):
        respx_mock.post("/api/api/propertydefinitions/derived").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("{a} + {b}", a=property_refs[0], b=property_refs[1]),
            is_filterable=False,
        )
        # when we call create
        state = sut.create(client)
        # then a post is made with the expected fields
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
            "propertyDescription": "description",
            "derivationFormula": "Properties[Instrument/refs/x] + Properties[Instrument/refs/y]",
            "isFilterable": False,
        }
        assert state == {"scope": "sc1", "code": "cd1", "domain": "Holding", "derived": True}

    def test_create_value_prop_datatype_ref(self, respx_mock):
        # create definition
        respx_mock.post("/api/api/propertydefinitions").mock(return_value=httpx.Response(200, json={}))
        # get datatype
        respx_mock.get("/api/api/datatypes/system/currency").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # given a references to a currency datatype that exists
        dt = datatype.DataTypeRef(id="dt", scope="system", code="currency")
        dt.attach(client)
        # when we use the datatype in the property definition
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=dt,
            property_description="description",
            life_time=property.LifeTime.Perpetual,
            constraint_style=property.ConstraintStyle.Property,
        )
        # when we call create
        state = sut.create(client)
        # then a post is made using the scope and code of the datatype
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "system", "code": "currency"},
            "propertyDescription": "description",
            "lifeTime": "Perpetual",
            "constraintStyle": "Property",
        }
        assert state == {"scope": "sc1", "code": "cd1", "domain": "Holding", "derived": False}

    def test_create_value_prop_datatype_resource(self, respx_mock):
        # create definition
        respx_mock.post("/api/api/propertydefinitions").mock(return_value=httpx.Response(200, json={}))
        # create datatype
        respx_mock.post("/api/api/datatypes").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        # given a datatype resource that gets created during the deploy
        dt = datatype.DataTypeResource(
            id="dt",
            scope="dtscope",
            code="dtcode",
            type_value_range=datatype.TypeValueRange.CLOSED,
            display_name="Priority Test",
            description="A test datatype for Priority",
            value_type=datatype.ValueType.STRING,
            acceptable_values=["High", "Medium", "Low"],
        )
        dt.create(client)
        # when we use the datatype in the property definition
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=dt,
            property_description="description",
            life_time=property.LifeTime.Perpetual,
            constraint_style=property.ConstraintStyle.Property,
        )
        # when we call create
        state = sut.create(client)
        # then a post is made using the scope and code of the datatype
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "dtscope", "code": "dtcode"},
            "propertyDescription": "description",
            "lifeTime": "Perpetual",
            "constraintStyle": "Property",
        }
        assert state == {"scope": "sc1", "code": "cd1", "domain": "Holding", "derived": False}

    @staticmethod
    def test_validates_no_is_filterable_on_value_prop():
        with pytest.raises(RuntimeError) as err:
            property.DefinitionResource(
                id="one",
                domain=property.Domain.Holding,
                scope="sc1",
                code="cd1",
                display_name="name",
                data_type_id=property.ResourceId(scope="ids", code="idc"),
                property_description="description",
                life_time=property.LifeTime.Perpetual,
                is_filterable=False,
            )
        assert (
            str(err.value)
            == "Cannot set 'is_filterable' field, a property must be either derived or plain"
        )

    @staticmethod
    def test_validates_no_lifetime_on_derived():
        with pytest.raises(RuntimeError):
            property.DefinitionResource(
                id="one",
                domain=property.Domain.Holding,
                scope="sc1",
                code="cd1",
                display_name="name",
                data_type_id=property.ResourceId(scope="ids", code="idc"),
                property_description="description",
                life_time=property.LifeTime.Perpetual,
                derivation_formula=property.Formula("3 + 4"),
            )

    @staticmethod
    def test_validates_no_constraint_on_derived():
        with pytest.raises(RuntimeError):
            property.DefinitionResource(
                id="one",
                domain=property.Domain.Holding,
                scope="sc1",
                code="cd1",
                display_name="name",
                data_type_id=property.ResourceId(scope="ids", code="idc"),
                property_description="description",
                constraint_style=property.ConstraintStyle.Identifier,
                derivation_formula=property.Formula("3 + 4"),
            )

    @staticmethod
    def test_validates_no_collection_on_derived():
        with pytest.raises(RuntimeError):
            property.DefinitionResource(
                id="one",
                domain=property.Domain.Holding,
                scope="sc1",
                code="cd1",
                display_name="name",
                data_type_id=property.ResourceId(scope="ids", code="idc"),
                property_description="description",
                collection_type=property.CollectionType.Set,
                derivation_formula=property.Formula("3 + 4"),
            )

    @staticmethod
    def test_value_prop_deps():
        # give a value property
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
        )
        # it has no dependencies
        assert sut.deps() == []

    @staticmethod
    def test_valueprop_datatype_deps():
        # given a datatype resource that gets created during the deploy
        dt = datatype.DataTypeResource(
            id="dt",
            scope="dtscope",
            code="dtcode",
            type_value_range=datatype.TypeValueRange.CLOSED,
            display_name="Priority Test",
            description="A test datatype for Priority",
            value_type=datatype.ValueType.STRING,
            acceptable_values=["High", "Medium", "Low"],
        )
        # and the property refers to the datatype
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=dt,
        )
        # the datatype is included in the deps of the property
        assert sut.deps() == [dt]

    @staticmethod
    def test_derived_prop_deps(property_refs):
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("{a} + {b}", a=property_refs[0], b=property_refs[1]),
        )
        assert sut.deps() == property_refs

    def test_formula_with_resource(self, respx_mock):
        respx_mock.post("/api/api/propertydefinitions/derived").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # given a value property
        used = property.DefinitionResource(
            id="two",
            domain=property.Domain.Instrument,
            scope="sc2",
            code="cd2",
            display_name="two",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
        )
        # and it is referenced in a formula on a derived prop
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("2 * {a}", a=used),
            is_filterable=True,
        )
        # and we call create
        sut.create(client)
        # then a post is made with identifier of used
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
            "propertyDescription": "description",
            "derivationFormula": "2 * Properties[Instrument/sc2/cd2]",
            "isFilterable": True,
        }

    def test_formula_with_non_resource(self, respx_mock):
        respx_mock.post("/api/api/propertydefinitions/derived").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # given a derived formula with numbers passed in
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("2 * {a}", a=17),
        )
        # and we call create
        sut.create(client)
        # then a post is made with identifier of used
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
            "propertyDescription": "description",
            "derivationFormula": "2 * 17",
        }
        # and the deps are empty
        assert sut.deps() == []

    def test_update_no_change(self, respx_mock):
        # given a derived property exists with y=2x17
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "domain": "Holding",
                    "scope": "sc1",
                    "code": "cd1",
                    "displayName": "name",
                    "dataTypeId": {"scope": "ids", "code": "idc"},
                    "propertyDescription": "description",
                    "derivationFormula": "2 * 17",
                    "isFilterable": False,
                },
            )
        )
        client = self.client
        # when we update it with a new formula
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("2 * {a}", a=17),
            is_filterable=False,
        )
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=True)
        state = sut.update(client, old_state)
        # the new state is None and no put was made
        assert state is None

    def test_update_valueprop_name(self, respx_mock):
        # given a derived property exists with y=2x17
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "domain": "Holding",
                    "scope": "sc1",
                    "code": "cd1",
                    "displayName": "name1",
                    "dataTypeId": {"scope": "ids", "code": "idc"},
                },
            )
        )
        # value url for the update
        respx_mock.put("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # when we update it with a new name
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name2",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
        )
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=False)
        state = sut.update(client, old_state)
        # then a put is made with the new formula
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name2",
            "dataTypeId": {"scope": "ids", "code": "idc"},
        }
        # and the state is returned
        assert state is not None

    def test_update_formula(self, respx_mock):
        # given a derived property exists with y=2x17
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "domain": "Holding",
                    "scope": "sc1",
                    "code": "cd1",
                    "displayName": "name",
                    "dataTypeId": {"scope": "ids", "code": "idc"},
                    "propertyDescription": "description",
                    "derivationFormula": "2 * 17",
                },
            )
        )
        respx_mock.put("/api/api/propertydefinitions/derived/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # when we update it with a new formula
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("3 * {a}", a=26),
        )
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=True)
        state = sut.update(client, old_state)
        # then a put is made with the new formula
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
            "propertyDescription": "description",
            "derivationFormula": "3 * 26",
        }
        # and the state is returned
        assert state is not None

    def test_update_is_filterable(self, respx_mock):
        # given a derived property exists with y=2x17
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "domain": "Holding",
                    "scope": "sc1",
                    "code": "cd1",
                    "displayName": "name",
                    "dataTypeId": {"scope": "ids", "code": "idc"},
                    "propertyDescription": "description",
                    "derivationFormula": "2 * 17",
                    "isFilterable": True,
                },
            )
        )
        respx_mock.put("/api/api/propertydefinitions/derived/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # when we update it with a new formula
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("2 * {a}", a=17),
            is_filterable=False,
        )
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=True)
        state = sut.update(client, old_state)
        # then a put is made with the new formula
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
            "propertyDescription": "description",
            "derivationFormula": "2 * 17",
            "isFilterable": False,
        }
        # and the state is returned
        assert state is not None

    def test_update_code(self, respx_mock):
        # delete using normal definition url
        respx_mock.delete("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        # create using derived url
        respx_mock.post("/api/api/propertydefinitions/derived").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # when we update it with a different code
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd2",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
            property_description="description",
            derivation_formula=property.Formula("3 * {a}", a=26),
        )
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=True)
        state = sut.update(client, old_state)
        # then a post is made with the new formula
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd2",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
            "propertyDescription": "description",
            "derivationFormula": "3 * 26",
        }
        # and the state is returned
        assert state is not None
        # and the delete was called

    def test_update_derived_to_value(self, respx_mock):
        # delete using normal definition url
        respx_mock.delete("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        # create using value url
        respx_mock.post("/api/api/propertydefinitions").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        # when we update it using the same scope/code but a value property
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="ids", code="idc"),
        )
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=True)
        state = sut.update(client, old_state)
        # then a post is made with the value property
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "ids", "code": "idc"},
        }
        # and the state is returned
        assert state == {"domain": "Holding", "scope": "sc1", "code": "cd1", "derived": False}
        # and the get and the delete are both called

    def test_update_data_type(self, respx_mock):
        # given a property exists with datatype=string
        respx_mock.get("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "domain": "Holding",
                    "scope": "sc1",
                    "code": "cd1",
                    "displayName": "name",
                    "dataTypeId": {"scope": "system", "code": "string"},
                },
            )
        )
        # delete using normal definition url
        respx_mock.delete("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        # create using value url
        respx_mock.post("/api/api/propertydefinitions").mock(return_value=httpx.Response(200, json={}))
        client = self.client
        # when we update it using the same scope/code but a number type
        sut = property.DefinitionResource(
            id="one",
            domain=property.Domain.Holding,
            scope="sc1",
            code="cd1",
            display_name="name",
            data_type_id=property.ResourceId(scope="system", code="number"),
        )
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=False)
        state = sut.update(client, old_state)
        # then a post is made with the new datatype
        req = respx_mock.calls.last.request
        assert json.loads(req.content) == {
            "domain": "Holding",
            "scope": "sc1",
            "code": "cd1",
            "displayName": "name",
            "dataTypeId": {"scope": "system", "code": "number"},
        }
        # and the state is returned
        assert state == {"domain": "Holding", "scope": "sc1", "code": "cd1", "derived": False}
        # and the get and the delete are both called

    def test_delete(self, respx_mock):
        # delete using normal definition url
        respx_mock.delete("/api/api/propertydefinitions/Holding/sc1/cd1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        # when we delete a property definition
        old_state = SimpleNamespace(domain="Holding", scope="sc1", code="cd1", derived=False)
        property.DefinitionResource.delete(client, old_state)
        # then the delete call is made
