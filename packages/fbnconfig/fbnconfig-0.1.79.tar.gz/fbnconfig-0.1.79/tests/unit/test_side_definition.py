import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import property, side_definition

TEST_BASE = "https://foo.lusid.com"


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeSideRef:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [lambda x: x.raise_for_status()]})

    def test_attach_when_present(self, respx_mock):
        # given that the remote definition exists
        respx_mock.get("/api/api/transactionconfiguration/sides/sd1?scope=sc1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = side_definition.SideRef(id="one", scope="sc1", side="sd1")
        # when we call attach
        sut.attach(client)
        # then a get request was made with the scope passed as a parameter
        req = respx_mock.calls.last.request
        assert dict(req.url.params) == {"scope": "sc1"}

    def test_attach_when_missing(self, respx_mock):
        # given the remote does not exist
        respx_mock.get("/api/api/transactionconfiguration/sides/sd2?scope=sc1").mock(
            return_value=httpx.Response(404, json={})
        )
        client = self.client
        sut = side_definition.SideRef(id="two", scope="sc1", side="sd2")
        # when we call attach an exception is raised
        with pytest.raises(RuntimeError) as ex:
            sut.attach(client)
        assert "Side sd2 does not exist in scope sc1" in str(ex.value)

    def test_attach_when_http_error(self, respx_mock):
        # given the server returns an error
        respx_mock.get("/api/api/transactionconfiguration/sides/sd3?scope=sc1").mock(
            return_value=httpx.Response(400, json={})
        )
        client = self.client
        sut = side_definition.SideRef(id="three", scope="sc1", side="sd3")
        # when we call attach an exception is raised
        with pytest.raises(httpx.HTTPError):
            sut.attach(client)


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeSideResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [lambda x: x.raise_for_status()]})

    @pytest.fixture
    def property_definition_refs(self):
        names = ["a", "b", "c", "d", "e", "f"]
        return [
            property.DefinitionRef(id=name, domain=property.Domain.Transaction, scope="sc1", code=name)
            for name in names
        ]

    @pytest.fixture
    def side_resource_side_1(self):
        return side_definition.SideResource(
            id="one",
            side="sd1",
            scope="sc1",
            security="Txn:LusidInstrumentId",
            currency="Txn:TradeCurrency",
            rate="Txn:TradeToPortfolioRate",
            units="Txn:Units",
            amount="Txn:TradeAmount",
            notional_amount="0",
        )

    @pytest.fixture
    def property_definition_resources(self):
        names = ["a", "b", "c", "d", "e", "f"]
        return [
            property.DefinitionResource(
                id=name,
                domain=property.Domain.Transaction,
                scope="sc1",
                code=name,
                display_name="Example Display Name",
                data_type_id=property.ResourceId(scope="system", code="number"),
                property_description="Example property description",
                life_time=property.LifeTime.Perpetual,
                constraint_style=property.ConstraintStyle.Property,
            )
            for name in names
        ]

    @pytest.fixture
    def definition_fixtures(self, request):
        return request.getfixturevalue(request.param)

    def test_create_side(self, respx_mock, side_resource_side_1):
        respx_mock.put("/api/api/transactionconfiguration/sides/sd1?scope=sc1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = side_resource_side_1
        state = sut.create(client)

        req = respx_mock.calls.last.request

        assert json.loads(req.content) == side_resource_side_1.model_dump(by_alias=True)
        assert state == {"side": "sd1", "scope": "sc1"}

    @pytest.mark.parametrize(
        "definition_fixtures",
        ["property_definition_refs", "property_definition_resources"],
        indirect=True,
    )
    def test_create_side_with_property_definitions(self, respx_mock, definition_fixtures):
        prop_resources = definition_fixtures

        respx_mock.put("/api/api/transactionconfiguration/sides/sd1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = side_definition.SideResource(
            id="one",
            side="sd1",
            scope="sc1",
            security=prop_resources[0],
            currency=prop_resources[1],
            rate=prop_resources[2],
            units=prop_resources[3],
            amount=prop_resources[4],
            notional_amount=prop_resources[5],
        )

        state = sut.create(client)

        req = respx_mock.calls.last.request
        assert sut.deps() == [
            prop_resources[0],
            prop_resources[1],
            prop_resources[4],
            prop_resources[2],
            prop_resources[3],
            prop_resources[5],
        ]

        assert json.loads(req.content) == {
            "side": "sd1",
            "security": "Transaction/sc1/a",
            "currency": "Transaction/sc1/b",
            "rate": "Transaction/sc1/c",
            "units": "Transaction/sc1/d",
            "amount": "Transaction/sc1/e",
            "notionalAmount": "Transaction/sc1/f",
        }
        assert state == {"side": "sd1", "scope": "sc1"}

    def test_create_side_with_mixed_definitions(
        self, respx_mock, property_definition_refs, property_definition_resources
    ):
        respx_mock.put("/api/api/transactionconfiguration/sides/sd1?scope=sc1").mock(
            return_value=httpx.Response(200, json={})
        )
        client = self.client
        sut = side_definition.SideResource(
            id="one",
            side="sd1",
            scope="sc1",
            security=property_definition_refs.pop(0),
            currency=property_definition_refs.pop(0),
            rate=property_definition_resources.pop(0),
            units=property_definition_resources.pop(0),
            amount="Txn:TradeAmount",
            notional_amount="0",
        )

        state = sut.create(client)

        req = respx_mock.calls.last.request

        assert sut.deps() == [
            property.DefinitionRef(id="a", domain=property.Domain.Transaction, scope="sc1", code="a"),
            property.DefinitionRef(id="b", domain=property.Domain.Transaction, scope="sc1", code="b"),
            property.DefinitionResource(
                id="a",
                domain=property.Domain.Transaction,
                scope="sc1",
                code="a",
                display_name="Example Display Name",
                data_type_id=property.ResourceId(scope="system", code="number"),
                property_description="Example property description",
                life_time=property.LifeTime.Perpetual,
                constraint_style=property.ConstraintStyle.Property,
            ),
            property.DefinitionResource(
                id="b",
                domain=property.Domain.Transaction,
                scope="sc1",
                code="b",
                display_name="Example Display Name",
                data_type_id=property.ResourceId(scope="system", code="number"),
                property_description="Example property description",
                life_time=property.LifeTime.Perpetual,
                constraint_style=property.ConstraintStyle.Property,
            ),
        ]

        assert json.loads(req.content) == {
            "side": "sd1",
            "security": "Transaction/sc1/a",
            "currency": "Transaction/sc1/b",
            "rate": "Transaction/sc1/a",
            "units": "Transaction/sc1/b",
            "amount": "Txn:TradeAmount",
            "notionalAmount": "0",
        }
        assert state == {"side": "sd1", "scope": "sc1"}

    def test_read_side(self, respx_mock, side_resource_side_1):
        respx_mock.get("/api/api/transactionconfiguration/sides/sd1?scope=sc1").mock(
            return_value=httpx.Response(200, json=side_resource_side_1.model_dump(by_alias=True))
        )

        client = self.client
        old_state = SimpleNamespace(scope="sc1", side="sd1")

        sut = side_resource_side_1

        remote = sut.read(client, old_state)
        assert remote == side_resource_side_1.model_dump(by_alias=True)
        assert {"scope": old_state.scope, "side": old_state.side} == {
            "scope": sut.scope,
            "side": sut.side,
        }

    def test_read_side_failure_not_found(self, respx_mock, side_resource_side_1):
        respx_mock.get("/api/api/transactionconfiguration/sides/sd1?scope=sc1").mock(
            return_value=httpx.Response(404)
        )
        old_state = SimpleNamespace(scope="sc1", side="sd1")
        client = self.client
        sut = side_resource_side_1

        with pytest.raises(httpx.HTTPStatusError):
            remote = sut.read(client, old_state)
            assert remote is None

    def test_delete_side(self, respx_mock, side_resource_side_1):
        respx_mock.delete("/api/api/transactionconfiguration/sides/sd1/$delete?scope=sc1").mock(
            return_value=httpx.Response(200)
        )
        client = self.client
        old_state = SimpleNamespace(scope="sc1", side="sd1")
        sut = side_resource_side_1

        sut.delete(client, old_state)

    def test_delete_side_missing(self, respx_mock, side_resource_side_1):
        respx_mock.delete("/api/api/transactionconfiguration/sides/sd1/$delete?scope=sc1").mock(
            return_value=httpx.Response(404)
        )
        client = self.client
        old_state = SimpleNamespace(scope="sc1", side="sd1")
        sut = side_resource_side_1

        with pytest.raises(httpx.HTTPStatusError):
            sut.delete(client, old_state)

    def test_update_side_no_change(self, respx_mock, side_resource_side_1):
        respx_mock.get("/api/api/transactionconfiguration/sides/sd1?scope=sc1").mock(
            return_value=httpx.Response(200, json=side_resource_side_1.model_dump(by_alias=True))
        )

        client = self.client

        sut = side_resource_side_1
        old_state = SimpleNamespace(scope="sc1", side="sd1")
        state = sut.update(client, old_state)
        assert state is None

    @pytest.mark.parametrize(
        "update_changes",
        [
            {
                "does_require_get": False,
                "put_side": "sd1",
                "put_scope": "sc2",
                "put_response": {
                    "side": "sd1",
                    "security": "Txn:LusidInstrumentId",
                    "currency": "Txn:TradeCurrency",
                    "rate": "Txn:TradeToPortfolioRate",
                    "units": "Txn:Units",
                    "amount": "Txn:TradeAmount",
                    "notionalAmount": "0",
                },
                "resource": side_definition.SideResource(
                    id="two",
                    side="sd1",
                    scope="sc2",
                    security="Txn:LusidInstrumentId",
                    currency="Txn:TradeCurrency",
                    rate="Txn:TradeToPortfolioRate",
                    units="Txn:Units",
                    amount="Txn:TradeAmount",
                    notional_amount="0",
                ),
            },
            {
                "does_require_get": False,
                "put_side": "sd2",
                "put_scope": "sc1",
                "put_response": {
                    "side": "sd2",
                    "security": "Txn:LusidInstrumentId",
                    "currency": "Txn:TradeCurrency",
                    "rate": "Txn:TradeToPortfolioRate",
                    "units": "Txn:Units",
                    "amount": "Txn:TradeAmount",
                    "notionalAmount": "0",
                },
                "resource": side_definition.SideResource(
                    id="two",
                    side="sd2",
                    scope="sc1",
                    security="Txn:LusidInstrumentId",
                    currency="Txn:TradeCurrency",
                    rate="Txn:TradeToPortfolioRate",
                    units="Txn:Units",
                    amount="Txn:TradeAmount",
                    notional_amount="0",
                ),
            },
            {
                "does_require_get": True,
                "put_side": "sd1",
                "put_scope": "sc1",
                "put_response": {
                    "side": "sd1",
                    "security": "Txn:TradeCurrency",
                    "currency": "Txn:TradeCurrency",
                    "rate": "Txn:TradeToPortfolioRate",
                    "units": "Txn:Units",
                    "amount": "Txn:TradeAmount",
                    "notionalAmount": "0",
                },
                "resource": side_definition.SideResource(
                    id="one",
                    side="sd1",
                    scope="sc1",
                    security="Txn:TradeCurrency",
                    currency="Txn:TradeCurrency",
                    rate="Txn:TradeToPortfolioRate",
                    units="Txn:Units",
                    amount="Txn:TradeAmount",
                    notional_amount="0",
                ),
                "get_side": "sd1",
                "get_scope": "sc1",
                "get_response": {
                    "side": "sd1",
                    "security": "Txn:LusidInstrumentId",
                    "currency": "Txn:TradeCurrency",
                    "rate": "Txn:TradeToPortfolioRate",
                    "units": "Txn:Units",
                    "amount": "Txn:TradeAmount",
                    "notionalAmount": "0",
                },
            },
        ],
    )
    def test_update_side(self, respx_mock, update_changes):
        respx_mock.put(
            f"/api/api/transactionconfiguration/sides/{update_changes['put_side']}?scope={update_changes['put_scope']}"
        ).mock(return_value=httpx.Response(200, json=update_changes["put_response"]))

        if update_changes["does_require_get"]:
            respx_mock.get(
                f"/api/api/transactionconfiguration/sides/{update_changes['get_side']}?scope={update_changes['get_scope']}"
            ).mock(return_value=httpx.Response(200, json=update_changes["get_response"]))
        else:
            respx_mock.delete("/api/api/transactionconfiguration/sides/sd1/$delete?scope=sc1").mock(
                return_value=httpx.Response(200)
            )

        client = self.client
        old_state = SimpleNamespace(scope="sc1", side="sd1")
        sut = update_changes["resource"]
        state = sut.update(client, old_state)

        if update_changes["does_require_get"]:
            req = respx_mock.calls.last.request
            assert state == {"scope": old_state.scope, "side": old_state.side}
            assert json.loads(req.content) == update_changes["put_response"]
        else:
            assert state != old_state

    def test_deps(self, property_definition_refs):
        sut = side_definition.SideResource(
            id="one",
            side="sd1",
            scope="sc1",
            security=property_definition_refs[0],
            currency=property_definition_refs[1],
            rate=property_definition_refs[2],
            units=property_definition_refs[2],
            amount="Txn:TradeAmount",
            notional_amount="0",
        )
        deps = sut.deps()
        assert deps == [
            property.DefinitionRef(id="a", domain=property.Domain.Transaction, scope="sc1", code="a"),
            property.DefinitionRef(id="b", domain=property.Domain.Transaction, scope="sc1", code="b"),
            property.DefinitionRef(id="c", domain=property.Domain.Transaction, scope="sc1", code="c"),
            property.DefinitionRef(id="c", domain=property.Domain.Transaction, scope="sc1", code="c"),
        ]
