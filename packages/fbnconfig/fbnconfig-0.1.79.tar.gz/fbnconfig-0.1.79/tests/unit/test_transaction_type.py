import json
from types import SimpleNamespace

import httpx
import pytest

from fbnconfig import property, side_definition, transaction_type

TEST_BASE = "https://foo.lusid.com"


@pytest.mark.respx(base_url=TEST_BASE)
class DescribeSideResource:
    client = httpx.Client(base_url=TEST_BASE, event_hooks={"response": [lambda x: x.raise_for_status()]})

    @pytest.fixture
    def simple_transaction_type(self):
        return transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_definition.SideResource(
                        id="side1",
                        side="Side1",
                        scope="sc1",
                        security="Txn:LusidInstrumentId",
                        currency="Txn:SettlementCurrency",
                        rate="Txn:TradeToPortfolioRate",
                        units="Txn:Units",
                        amount="Txn:TotalConsideration",
                        notional_amount="0",
                    ),
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                )
            ],
            calculations=[],
            properties=[],
        )

    @pytest.fixture
    def simple_transaction_type_no_movement_option(self):
        return transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_definition.SideResource(
                        id="side1",
                        side="Side1",
                        scope="sc1",
                        security="Txn:LusidInstrumentId",
                        currency="Txn:SettlementCurrency",
                        rate="Txn:TradeToPortfolioRate",
                        units="Txn:Units",
                        amount="Txn:TotalConsideration",
                        notional_amount="0",
                    ),
                    direction=1,
                    name="Stock Movement",
                    settlement_mode=transaction_type.SettlementMode.Internal,
                )
            ],
            calculations=[],
            properties=[],
        )

    @pytest.fixture
    def complex_transaction_type(self):
        transaction_configuration_properties = [
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd4"
                ),
                label_value="Hello world",
            ),
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd5"
                ),
                metric_value=transaction_type.MetricValue(value=1.23456, unit="GBP"),
            ),
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd6"
                ),
                label_set_value=["one", "two", "three"],
            ),
        ]

        return transaction_type.TransactionTypeResource(
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Test buy 1",
                    transaction_class="ConfigurationTest",
                    transaction_roles="AllRoles",
                    is_default=False,
                ),
                transaction_type.TransactionTypeAlias(
                    type="BY",
                    description="Test buy 2",
                    transaction_class="ConfigurationTest",
                    transaction_roles="AllRoles",
                    is_default=False,
                ),
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_definition.SideRef(id="side1", side="Side1", scope="sc1"),
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    mappings=[
                        transaction_type.TransactionTypePropertyMapping(
                            property_key=property.DefinitionRef(
                                id="one", domain=property.Domain.Transaction, scope="sc1", code="cd1"
                            ),
                            set_to="Hello world",
                        ),
                        transaction_type.TransactionTypePropertyMapping(
                            property_key=property.DefinitionRef(
                                id="two", domain=property.Domain.Transaction, scope="sc1", code="cd2"
                            ),
                            map_from=property.DefinitionRef(
                                id="three", domain=property.Domain.Transaction, scope="sc1", code="cd3"
                            ),
                        ),
                    ],
                    properties=transaction_configuration_properties,
                    settlement_mode=transaction_type.SettlementMode.Internal,
                )
            ],
            calculations=[
                transaction_type.TransactionTypeCalculation(
                    type=transaction_type.CalculationType.TaxAmounts,
                    side=side_definition.SideRef(id="side1", side="Side1", scope="sc1"),
                ),
                transaction_type.TransactionTypeCalculation(
                    type=transaction_type.CalculationType.NotionalAmount
                ),
            ],
            properties=transaction_configuration_properties,
            id="txn1",
            scope="sc1",
            source="default",
        )

    def test_read_transaction_type(self, respx_mock, simple_transaction_type):
        respx_mock.get(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(
            return_value=httpx.Response(
                200,
                json=simple_transaction_type.model_dump(mode="json", exclude_none=True, by_alias=True),
            )
        )

        client = self.client
        old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc1")

        sut = simple_transaction_type

        response = sut.read(client, old_state)
        assert response == {
            "aliases": [
                {
                    "type": "Buy",
                    "description": "Something",
                    "transactionClass": "default",
                    "transactionRoles": "LongLonger",
                    "isDefault": False,
                }
            ],
            "movements": [
                {
                    "movementTypes": "StockMovement",
                    "side": "Side1",
                    "direction": 1,
                    "properties": {},
                    "mappings": [],
                    "name": "Stock Movement",
                    "movementOptions": ["DirectAdjustment"],
                    "condition": "",
                    "settlementMode": "Internal",
                }
            ],
            "properties": {},
            "calculations": [],
        }

        assert {
            "transaction_type": old_state.transaction_type,
            "source": old_state.source,
            "scope": old_state.scope,
        } == {"transaction_type": "Buy", "source": "default", "scope": "sc1"}

    def test_read_transaction_type_missing(self, respx_mock, simple_transaction_type):
        respx_mock.get(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(return_value=httpx.Response(404))

        client = self.client
        with pytest.raises(httpx.HTTPError):
            old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc1")
            sut = simple_transaction_type
            sut.read(client, old_state)

    def test_create_transaction_type(self, respx_mock, simple_transaction_type):
        respx_mock.put(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(
            return_value=httpx.Response(
                200, json={"source": "default", "scope": "sc1", "transaction_type": "Buy"}
            )
        )

        client = self.client
        sut = simple_transaction_type

        state = sut.create(client)
        req = respx_mock.calls.last.request

        assert json.loads(req.content) == {
            "aliases": [
                {
                    "type": "Buy",
                    "description": "Something",
                    "transactionClass": "default",
                    "transactionRoles": "LongLonger",
                    "isDefault": False,
                }
            ],
            "movements": [
                {
                    "movementTypes": "StockMovement",
                    "side": "Side1",
                    "direction": 1,
                    "properties": {},
                    "mappings": [],
                    "name": "Stock Movement",
                    "movementOptions": ["DirectAdjustment"],
                    "condition": "",
                    "settlementMode": "Internal",
                }
            ],
            "properties": {},
            "calculations": [],
        }
        assert state == {"source": "default", "scope": "sc1", "transaction_type": "Buy"}

    def test_delete_transaction_type(self, respx_mock, simple_transaction_type):
        respx_mock.delete(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(return_value=httpx.Response(200))
        client = self.client
        old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc1")
        sut = simple_transaction_type

        sut.delete(client, old_state)

    def test_delete_transaction_type_missing(self, respx_mock, simple_transaction_type):
        respx_mock.delete(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(return_value=httpx.Response(404))
        client = self.client
        with pytest.raises(httpx.HTTPError):
            old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc1")
            sut = simple_transaction_type
            sut.delete(client, old_state)

    def test_update_transaction_type_no_change(self, respx_mock, simple_transaction_type):
        respx_mock.get(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "aliases": [
                        {
                            "type": "Buy",
                            "description": "Something",
                            "transactionClass": "default",
                            "transactionRoles": "LongLonger",
                            "isDefault": False,
                        }
                    ],
                    "movements": [
                        {
                            "movementTypes": "StockMovement",
                            "side": "Side1",
                            "direction": 1,
                            "properties": {},
                            "mappings": [],
                            "name": "Stock Movement",
                            "movementOptions": ["DirectAdjustment"],
                            "condition": "",
                            "settlementMode": "Internal",
                        }
                    ],
                    "properties": {},
                    "calculations": [],
                },
            )
        )

        client = self.client
        old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc1")
        sut = simple_transaction_type

        state = sut.update(client, old_state)

        assert state is None

    def test_update_transaction_type_no_change_no_movement_option(
        self, respx_mock, simple_transaction_type_no_movement_option
    ):
        respx_mock.get(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type_no_movement_option.source}/"
            f"{simple_transaction_type_no_movement_option._get_first_alias()}"
            f"?scope={simple_transaction_type_no_movement_option.scope}"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "aliases": [
                        {
                            "type": "Buy",
                            "description": "Something",
                            "transactionClass": "default",
                            "transactionRoles": "LongLonger",
                            "isDefault": False,
                        }
                    ],
                    "movements": [
                        {
                            "movementTypes": "StockMovement",
                            "side": "Side1",
                            "direction": 1,
                            "properties": {},
                            "mappings": [],
                            "name": "Stock Movement",
                            "movementOptions": [],
                            "condition": "",
                            "settlementMode": "Internal",
                        }
                    ],
                    "properties": {},
                    "calculations": [],
                },
            )
        )

        client = self.client
        old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc1")
        sut = simple_transaction_type_no_movement_option

        state = sut.update(client, old_state)

        assert state is None

    def test_update_transaction_type_state_change(self, respx_mock, simple_transaction_type):
        respx_mock.delete(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope=sc2"
        ).mock(return_value=httpx.Response(200))

        respx_mock.put(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(
            return_value=httpx.Response(
                200, json={"source": "default", "scope": "sc1", "transaction_type": "Buy"}
            )
        )

        client = self.client

        old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc2")
        sut = simple_transaction_type
        state = sut.update(client, old_state)
        assert state == {"source": "default", "scope": "sc1", "transaction_type": "Buy"}

    def test_update_transaction_type_content_changed(self, respx_mock, simple_transaction_type):
        respx_mock.get(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(
            return_value=httpx.Response(
                200,
                json=simple_transaction_type.model_dump(mode="json", exclude_none=True, by_alias=True),
            )
        )

        respx_mock.put(
            f"/api/api/transactionconfiguration/types/{simple_transaction_type.source}/{simple_transaction_type._get_first_alias()}?scope={simple_transaction_type.scope}"
        ).mock(
            return_value=httpx.Response(
                200, json={"source": "default", "scope": "sc1", "transaction_type": "Buy"}
            )
        )

        client = self.client

        old_state = SimpleNamespace(transaction_type="Buy", source="default", scope="sc1")

        sut = simple_transaction_type

        sut.movements = []
        state = sut.update(client, old_state)
        assert state == {"source": "default", "scope": "sc1", "transaction_type": "Buy"}

    def test_deps_movements_unique(self):
        side_resource = side_definition.SideResource(
            id="side1",
            side="Side1",
            scope="sc1",
            security="Txn:LusidInstrumentId",
            currency="Txn:SettlementCurrency",
            rate="Txn:TradeToPortfolioRate",
            units="Txn:Units",
            amount="Txn:TotalConsideration",
            notional_amount="0",
        )

        side_ref = side_definition.SideRef(id="side1", side="Side1", scope="sc1")

        txn_type_no_movements = transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[],
            calculations=[],
            properties=[],
        )

        txn_type_side_resource_movement = transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_resource,
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                ),
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_resource,
                    direction=1,
                    name="Stock Movement 2",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                ),
            ],
            calculations=[],
            properties=[],
        )

        txn_type_side_ref_movement = transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_ref,
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                ),
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_ref,
                    direction=1,
                    name="Stock Movement 2",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                ),
            ],
            calculations=[],
            properties=[],
        )

        deps_no_movements = txn_type_no_movements.deps()
        deps_side_resource_movement = txn_type_side_resource_movement.deps()
        deps_side_ref_movement = txn_type_side_ref_movement.deps()

        assert deps_no_movements == []
        assert deps_side_resource_movement == [side_resource]
        assert deps_side_ref_movement == [side_ref]

    def test_deps_movement_properties_unique(self):
        transaction_configuration_properties = [
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionResource(
                    id="pd1",
                    domain=property.Domain.TransactionConfiguration,
                    scope="sc1",
                    code="pd1",
                    display_name="property",
                    data_type_id=property.ResourceId(scope="system", code="number"),
                    constraint_style=property.ConstraintStyle.Property,
                    property_description="property",
                    life_time=property.LifeTime.Perpetual,
                    collection_type=None,
                ),
                label_value="Hello world",
            ),
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd5"
                ),
                metric_value=transaction_type.MetricValue(value=1.23456, unit="GBP"),
            ),
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd5"
                ),
                label_set_value=["one", "two", "three"],
            ),
        ]

        side_ref = side_definition.SideRef(id="side1", side="Side1", scope="sc1")

        txn_type = transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_ref,
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    properties=None,
                    settlement_mode=transaction_type.SettlementMode.Internal,
                )
            ],
            calculations=[],
            properties=[],
        )

        assert txn_type.deps() == [side_ref]

        txn_type.movements[0].properties = transaction_configuration_properties

        assert txn_type.deps() == [
            side_ref,
            property.DefinitionResource(
                id="pd1",
                domain=property.Domain.TransactionConfiguration,
                scope="sc1",
                code="pd1",
                display_name="property",
                data_type_id=property.ResourceId(scope="system", code="number"),
                constraint_style=property.ConstraintStyle.Property,
                property_description="property",
                life_time=property.LifeTime.Perpetual,
                collection_type=None,
            ),
            property.DefinitionRef(
                id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd5"
            ),
        ]

    def test_deps_movements_mappings_unique(self):
        side_ref = side_definition.SideRef(id="side1", side="Side1", scope="sc1")

        mappings = [
            transaction_type.TransactionTypePropertyMapping(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.Transaction, scope="sc1", code="cd1"
                ),
                set_to="Hello world",
            ),
            transaction_type.TransactionTypePropertyMapping(
                property_key=property.DefinitionRef(
                    id="two", domain=property.Domain.Transaction, scope="sc1", code="cd2"
                ),
                map_from=property.DefinitionRef(
                    id="three", domain=property.Domain.Transaction, scope="sc1", code="cd3"
                ),
            ),
        ]

        txn_type = transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_ref,
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                )
            ],
            calculations=[],
            properties=[],
        )

        assert txn_type.deps() == [side_ref]

        txn_type.movements[0].mappings = mappings

        assert txn_type.deps() == [
            side_ref,
            property.DefinitionRef(
                id="one", domain=property.Domain.Transaction, scope="sc1", code="cd1"
            ),
            property.DefinitionRef(
                id="two", domain=property.Domain.Transaction, scope="sc1", code="cd2"
            ),
            property.DefinitionRef(
                id="three", domain=property.Domain.Transaction, scope="sc1", code="cd3"
            ),
        ]

    def test_deps_properties_unique(self):
        side_ref = side_definition.SideRef(id="side1", side="Side1", scope="sc1")

        properties = [
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd1"
                ),
                label_value="Hello world",
            ),
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="two", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd2"
                ),
                metric_value=transaction_type.MetricValue(value=1.23456, unit="GBP"),
            ),
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="two", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd2"
                ),
                label_set_value=["one", "two", "three"],
            ),
        ]

        txn_type = transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_ref,
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                )
            ],
            calculations=[],
            properties=[],
        )

        assert txn_type.deps() == [side_ref]

        txn_type.properties = properties

        assert txn_type.deps() == [
            side_ref,
            property.DefinitionRef(
                id="one", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd1"
            ),
            property.DefinitionRef(
                id="two", domain=property.Domain.TransactionConfiguration, scope="sc1", code="cd2"
            ),
        ]

    def test_deps_calculations_unique(self):
        side_ref = side_definition.SideRef(id="side1", side="Side1", scope="sc1")

        side_resource = side_definition.SideResource(
            id="side2",
            side="Side2",
            scope="sc2",
            security="Txn:LusidInstrumentId",
            currency="Txn:SettlementCurrency",
            rate="Txn:TradeToPortfolioRate",
            units="Txn:Units",
            amount="Txn:TotalConsideration",
            notional_amount="0",
        )

        calculations = [
            transaction_type.TransactionTypeCalculation(
                type=transaction_type.CalculationType.TaxAmounts, side=side_ref
            ),
            transaction_type.TransactionTypeCalculation(
                type=transaction_type.CalculationType.ExchangeRate, side=side_ref
            ),
            transaction_type.TransactionTypeCalculation(
                type=transaction_type.CalculationType.TaxAmounts, side=side_resource
            ),
            transaction_type.TransactionTypeCalculation(
                type=transaction_type.CalculationType.NotionalAmount
            ),
        ]

        txn_type = transaction_type.TransactionTypeResource(
            id="txn1",
            scope="sc1",
            source="default",
            aliases=[
                transaction_type.TransactionTypeAlias(
                    type="Buy",
                    description="Something",
                    transaction_class="default",
                    transaction_roles="LongLonger",
                    is_default=False,
                )
            ],
            movements=[
                transaction_type.TransactionTypeMovement(
                    movement_types=transaction_type.MovementType.StockMovement,
                    side=side_ref,
                    direction=1,
                    name="Stock Movement",
                    movement_options=[transaction_type.MovementOption.DirectAdjustment],
                    settlement_mode=transaction_type.SettlementMode.Internal,
                )
            ],
            calculations=[],
            properties=[],
        )

        assert txn_type.deps() == [side_ref]

        txn_type.calculations = calculations

        assert txn_type.deps() == [side_ref, side_resource]

    def test_transaction_type_property_only_one_exists(self):
        # When we set more than one of label_value, label_set_value or metric_value
        # on a property, an error is thrown
        with pytest.raises(KeyError):
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.Transaction, scope="sc1", code="cd1"
                ),
                label_value="Hello world",
                metric_value=transaction_type.MetricValue(value=1.23456, unit="GBP"),
            )

        # If three exist, throw error
        with pytest.raises(KeyError):
            transaction_type.PerpetualProperty(
                property_key=property.DefinitionRef(
                    id="one", domain=property.Domain.Transaction, scope="sc1", code="cd1"
                ),
                label_value="Hello world",
                label_set_value=["Hello", "World"],
                metric_value=transaction_type.MetricValue(value=1.23456, unit="GBP"),
            )

        # When one exists, it builds without error
        transaction_type.PerpetualProperty(
            property_key=property.DefinitionRef(
                id="one", domain=property.Domain.Transaction, scope="sc1", code="cd1"
            ),
            metric_value=transaction_type.MetricValue(value=1.23456, unit="GBP"),
        )

    def test_no_aliases_throws_value_error(self):
        with pytest.raises(ValueError):
            transaction_type.TransactionTypeResource(
                id="txn1", scope="sc1", source="default", aliases=[]
            )

    def test_complex_transaction_type_serializes_correctly(self, complex_transaction_type):
        assert complex_transaction_type.model_dump(mode="json", exclude_none=True, by_alias=True) == {
            "aliases": [
                {
                    "type": "Buy",
                    "description": "Test buy 1",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
                {
                    "type": "BY",
                    "description": "Test buy 2",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
            ],
            "movements": [
                {
                    "movementTypes": "StockMovement",
                    "side": "Side1",
                    "direction": 1,
                    "properties": {
                        "TransactionConfiguration/sc1/cd4": {
                            "key": "TransactionConfiguration/sc1/cd4",
                            "value": {"labelValue": "Hello world"},
                        },
                        "TransactionConfiguration/sc1/cd5": {
                            "key": "TransactionConfiguration/sc1/cd5",
                            "value": {"metricValue": {"value": 1.23456, "unit": "GBP"}},
                        },
                        "TransactionConfiguration/sc1/cd6": {
                            "key": "TransactionConfiguration/sc1/cd6",
                            "value": {"labelSetValue": ["one", "two", "three"]},
                        },
                    },
                    "mappings": [
                        {"propertyKey": "Transaction/sc1/cd1", "setTo": "Hello world"},
                        {"propertyKey": "Transaction/sc1/cd2", "mapFrom": "Transaction/sc1/cd3"},
                    ],
                    "name": "Stock Movement",
                    "movementOptions": ["DirectAdjustment"],
                    "condition": "",
                    "settlementMode": "Internal",
                }
            ],
            "properties": {
                "TransactionConfiguration/sc1/cd4": {
                    "key": "TransactionConfiguration/sc1/cd4",
                    "value": {"labelValue": "Hello world"},
                },
                "TransactionConfiguration/sc1/cd5": {
                    "key": "TransactionConfiguration/sc1/cd5",
                    "value": {"metricValue": {"value": 1.23456, "unit": "GBP"}},
                },
                "TransactionConfiguration/sc1/cd6": {
                    "key": "TransactionConfiguration/sc1/cd6",
                    "value": {"labelSetValue": ["one", "two", "three"]},
                },
            },
            "calculations": [{"type": "TaxAmounts", "side": "Side1"}, {"type": "Txn:NotionalAmount"}],
        }

    def test_equal_json_with_different_ordering(self):
        json1 = {
            "aliases": [
                {
                    "type": "ZZZZBuy",
                    "description": "Test buy 1",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
                {
                    "type": "BY",
                    "description": "Test buy 2",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
            ],
            "calculations": [
                {"type": "TaxAmounts", "side": "Side1"},
                {"type": "AAAAATaxAmounts", "side": "Side1"},
            ],
        }

        json2 = {
            "aliases": [
                {
                    "type": "BY",
                    "description": "Test buy 2",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
                {
                    "type": "ZZZZBuy",
                    "description": "Test buy 1",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
            ],
            "calculations": [
                {"type": "AAAAATaxAmounts", "side": "Side1"},
                {"type": "TaxAmounts", "side": "Side1"},
            ],
        }

        assert transaction_type._compare_json_structures(json1, json2)

    def test_not_equal_json(self):
        json1 = {
            "aliases": [
                {
                    "type": "ZZZZBuy",
                    "description": "Test buy 1",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
                {
                    "type": "BY",
                    "description": "Test buy 2",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
            ]
        }

        json2 = {
            "aliases": [
                {
                    "type": "BY",
                    "description": "Test buy 2",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": False,
                },
                {
                    "type": "ZZZZBuy",
                    "description": "Test buy 1",
                    "transactionClass": "ConfigurationTest",
                    "transactionRoles": "AllRoles",
                    "isDefault": True,  # Difference here
                },
            ]
        }

        assert not transaction_type._compare_json_structures(json1, json2)

    def test_nested_json_with_different_ordering(self):
        json1 = {
            "movements": [
                {
                    "movementTypes": "StockMovement",
                    "side": "Side1",
                    "direction": 1,
                    "properties": {
                        "TransactionConfiguration/sc1/cd4": {
                            "key": "TransactionConfiguration/sc1/cd4",
                            "value": {"labelValue": "Hello world"},
                        },
                        "TransactionConfiguration/sc1/cd5": {
                            "key": "TransactionConfiguration/sc1/cd5",
                            "value": {"metricValue": {"value": 1.23456, "unit": "GBP"}},
                        },
                    },
                    "mappings": [
                        {"propertyKey": "Transaction/sc1/cd2", "mapFrom": "Transaction/sc1/cd3"},
                        {"propertyKey": "Transaction/sc1/cd1", "setTo": "Hello world"},
                    ],
                    "name": "Stock Movement",
                    "movementOptions": ["IncludeTaxLots", "DirectAdjustment"],
                    "condition": "",
                    "settlementMode": "Internal",
                }
            ]
        }

        json2 = {
            "movements": [
                {
                    "movementTypes": "StockMovement",
                    "side": "Side1",
                    "direction": 1,
                    "properties": {
                        "TransactionConfiguration/sc1/cd5": {
                            "key": "TransactionConfiguration/sc1/cd5",
                            "value": {"metricValue": {"value": 1.23456, "unit": "GBP"}},
                        },
                        "TransactionConfiguration/sc1/cd4": {
                            "key": "TransactionConfiguration/sc1/cd4",
                            "value": {"labelValue": "Hello world"},
                        },
                    },
                    "mappings": [
                        {"propertyKey": "Transaction/sc1/cd1", "setTo": "Hello world"},
                        {"propertyKey": "Transaction/sc1/cd2", "mapFrom": "Transaction/sc1/cd3"},
                    ],
                    "name": "Stock Movement",
                    "movementOptions": ["DirectAdjustment", "IncludeTaxLots"],
                    "condition": "",
                    "settlementMode": "Internal",
                }
            ]
        }

        assert transaction_type._compare_json_structures(json1, json2)

    def test_different_json_structure(self):
        json1 = {
            "movements": [
                {
                    "movementTypes": "StockMovement",
                    "side": "Side1",
                    "direction": 1,
                    "settlementMode": "Internal",
                }
            ]
        }

        json2 = {
            "movements": [
                {
                    "movementTypes": "StockMovement",
                    "side": "Side2",  # Different side
                    "direction": 1,
                    "settlementMode": "Internal",
                }
            ]
        }

        assert not transaction_type._compare_json_structures(json1, json2)
