# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""System tests for Electricity Trading API."""
import asyncio
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Generator

import grpc
import pytest

from frequenz.client.electricity_trading import (
    Client,
    Currency,
    DeliveryArea,
    DeliveryPeriod,
    EnergyMarketCodeType,
    MarketSide,
    OrderDetail,
    OrderState,
    OrderType,
    Power,
    Price,
)

API_KEY = os.getenv("API_KEY", None)
if not API_KEY:
    raise ValueError("API Key is not set")
GRIDPOOL_ID = os.getenv("GRIDPOOL_ID", None)
if not GRIDPOOL_ID:
    raise ValueError("Gridpool ID is not set")
GRIDPOOL_ID = int(GRIDPOOL_ID)
SERVER_URL = "grpc://electricity-trading-testing.api.frequenz.com:443?ssl=true"

MIN_QUANTITY_MW = Decimal("0.1")
MIN_PRICE = Decimal(-9999.0)
MAX_PRICE = Decimal(9999.0)


class _TestTrader:
    """A test trader that provides a client and some common parameters for tests."""

    def __init__(self) -> None:
        self.client = Client(
            server_url=SERVER_URL,
            auth_key=API_KEY,
        )

        self.delivery_area = DeliveryArea(
            code="10YDE-EON------1", code_type=EnergyMarketCodeType.EUROPE_EIC
        )
        # Setting delivery start to the next whole hour after two hours from now
        self.delivery_start = (datetime.now(timezone.utc) + timedelta(hours=3)).replace(
            minute=0, second=0, microsecond=0
        )
        self.delivery_period = DeliveryPeriod(
            start=self.delivery_start,
            duration=timedelta(minutes=15),
        )
        self.price = Price(amount=Decimal("56"), currency=Currency.EUR)
        self.quantity = Power(mw=Decimal("0.1"))
        self.order_type = OrderType.LIMIT
        self.valid_until = None

    async def _reconnect(self) -> None:
        """Reconnect the client to the server."""
        await self.client.disconnect()
        self.client.connect()


@pytest.fixture
async def trader() -> _TestTrader:
    """Set up the test suite."""
    trader = _TestTrader()

    # The event loop is scoped to each test function.
    # And the gRPC client is a singleton and its internal state can be
    # corrupted when used concurrently from multiple async contexts.
    # Reconnecting ensures that the client is in a clean state for each test.
    await trader._reconnect()

    return trader


async def create_test_order(
    trader: _TestTrader,
    side: MarketSide = MarketSide.BUY,
    price: Price | None = None,
    quantity: Power | None = None,
    delivery_period: DeliveryPeriod | None = None,
    delivery_area: DeliveryArea | None = None,
    order_type: OrderType | None = None,
    valid_until: datetime | None = None,
) -> OrderDetail:
    """Create a test order with customizable parameters."""
    order_price = price or trader.price
    order_quantity = quantity or trader.quantity
    order_delivery_period = delivery_period or trader.delivery_period
    order_delivery_area = delivery_area or trader.delivery_area
    order_type = order_type or trader.order_type
    order_valid_until = valid_until or trader.valid_until
    order = await trader.client.create_gridpool_order(
        gridpool_id=GRIDPOOL_ID,
        delivery_area=order_delivery_area,
        delivery_period=order_delivery_period,
        order_type=order_type,
        side=side,
        price=order_price,
        quantity=order_quantity,
        valid_until=order_valid_until,
        tag="api-integration-test",
    )
    return order  # type: ignore


async def create_test_trade(
    trader: _TestTrader,
) -> tuple[OrderDetail, OrderDetail]:
    """
    Create identical orders on opposite sides to try to trigger a trade.

    Args:
        trader: The test trader for creating orders.

    Returns:
        A tuple of the created buy and sell orders.
    """
    # Set a different delivery period so that it is the only trade retrieved
    # It should also be < 9 hours from now since EPEX's intraday order book opens at 15:00
    delivery_start = (datetime.now(timezone.utc) + timedelta(hours=2)).replace(
        minute=0, second=0, microsecond=0
    )
    delivery_period = DeliveryPeriod(
        start=delivery_start,
        duration=timedelta(minutes=15),
    )
    buy_order = await create_test_order(
        trader=trader,
        delivery_period=delivery_period,
        side=MarketSide.BUY,
        price=Price(amount=Decimal("33"), currency=Currency.EUR),
    )

    sell_order = await create_test_order(
        trader=trader,
        delivery_period=delivery_period,
        side=MarketSide.SELL,
        price=Price(amount=Decimal("33"), currency=Currency.EUR),
    )

    return buy_order, sell_order


async def test_create_and_get_order(trader: _TestTrader) -> None:
    """Test creating a gridpool order and ensure it exists in the system."""
    # Create an order first
    order = await create_test_order(trader)
    assert order is not None, "Order creation failed"

    # Fetch order to check it exists remotely
    fetched_order = await trader.client.get_gridpool_order(
        GRIDPOOL_ID, order_id=order.order_id
    )

    assert fetched_order.order == order.order, "Order mismatch"


async def test_create_order_invalid_delivery_start_one_day_ago(
    trader: _TestTrader,
) -> None:
    """Test creating an order with a passed delivery start (one day ago)."""
    # Create an order with a delivery start in the past
    delivery_start = (datetime.now(timezone.utc) - timedelta(days=1)).replace(
        minute=0, second=0, microsecond=0
    )
    delivery_period = DeliveryPeriod(
        start=delivery_start,
        duration=timedelta(minutes=15),
    )
    with pytest.raises(ValueError, match="delivery_period must be in the future"):
        await create_test_order(trader, delivery_period=delivery_period)


async def test_create_order_invalid_delivery_start_one_hour_ago(
    trader: _TestTrader,
) -> None:
    """Test creating an order with a passed delivery start (one hour ago)."""
    # Create an order with a delivery start in the past
    delivery_start = (datetime.now(timezone.utc) - timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
    delivery_period = DeliveryPeriod(
        start=delivery_start,
        duration=timedelta(minutes=15),
    )
    with pytest.raises(ValueError, match="delivery_period must be in the future"):
        await create_test_order(trader, delivery_period=delivery_period)


async def test_create_order_invalid_delivery_start_15_minutes_ago(
    trader: _TestTrader,
) -> None:
    """Test creating an order with a passed delivery start (15 minutes ago)."""
    # Create an order with a delivery start in the past
    delivery_start = (datetime.now(timezone.utc) - timedelta(minutes=15)).replace(
        minute=0, second=0, microsecond=0
    )
    delivery_period = DeliveryPeriod(
        start=delivery_start,
        duration=timedelta(minutes=15),
    )
    with pytest.raises(ValueError, match="delivery_period must be in the future"):
        await create_test_order(trader, delivery_period=delivery_period)


async def test_create_order_invalid_valid_until_one_hour_ago(
    trader: _TestTrader,
) -> None:
    """Test creating an order with a passed valid until (one hour ago)."""
    valid_until = (datetime.now(timezone.utc) - timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
    with pytest.raises(ValueError, match="valid_until must be in the future"):
        await create_test_order(trader, valid_until=valid_until)


async def test_list_gridpool_orders(trader: _TestTrader) -> None:
    """Test listing gridpool orders and ensure they exist in the system."""
    # Create several orders
    created_orders_id = [(await create_test_order(trader)).order_id for _ in range(10)]

    # List the orders and check they are present
    # filter by delivery period to avoid fetching too many orders
    orders = [
        order
        async for order in trader.client.list_gridpool_orders(
            gridpool_id=GRIDPOOL_ID, delivery_period=trader.delivery_period
        )
    ]
    listed_orders_id = [order.order_id for order in orders]
    for order_id in created_orders_id:
        assert order_id in listed_orders_id, f"Order ID {order_id} not found"


async def test_update_order_price(trader: _TestTrader) -> None:
    """Test updating the price of an order."""
    # Create an order first
    order = await create_test_order(trader)

    # Update the order price and check the update was successful
    new_price = Price(amount=Decimal("50"), currency=Currency.EUR)
    updated_order = await trader.client.update_gridpool_order(
        gridpool_id=GRIDPOOL_ID, order_id=order.order_id, price=new_price
    )

    assert updated_order.order.price.amount == new_price.amount, "Price update failed"
    fetched_order = await trader.client.get_gridpool_order(
        GRIDPOOL_ID, order_id=order.order_id
    )
    assert (
        fetched_order.order.price.amount == updated_order.order.price.amount
    ), "Fetched price mismatch after update"
    assert (
        order.order.price.amount != new_price.amount
    ), "Original price should not be the same as the updated price"


async def test_update_order_quantity_failure(trader: _TestTrader) -> None:
    """Test updating the quantity of an order and ensure it fails."""
    # Create an order first
    order = await create_test_order(trader)

    quantity = Power(mw=Decimal("10"))

    # Expected failure as quantity update is not supported
    with pytest.raises(grpc.aio.AioRpcError) as excinfo:
        await trader.client.update_gridpool_order(
            gridpool_id=GRIDPOOL_ID, order_id=order.order_id, quantity=quantity
        )

    assert str(excinfo.value.details()) == "Updating 'quantity' is not allowed."
    assert (
        excinfo.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    ), "Expected INVALID_ARGUMENT error"


async def test_cancel_order(trader: _TestTrader) -> None:
    """Test cancelling an order."""
    # Create the order to be cancelled
    order = await create_test_order(trader)

    # Cancel the created order and ensure it's cancelled
    cancelled_order = await trader.client.cancel_gridpool_order(
        GRIDPOOL_ID, order_id=order.order_id
    )
    assert cancelled_order.order_id == order.order_id, "Order cancellation failed"

    fetched_order = await trader.client.get_gridpool_order(
        GRIDPOOL_ID, order_id=order.order_id
    )
    assert (
        fetched_order.state_detail.state == OrderState.CANCELED
    ), "Order state should be CANCELED"


async def test_update_cancelled_order_failure(trader: _TestTrader) -> None:
    """Test updating a cancelled order and ensure it fails."""
    # Create an order first
    order = await create_test_order(trader)

    # Cancel the created order
    await trader.client.cancel_gridpool_order(GRIDPOOL_ID, order_id=order.order_id)

    # Expected failure as cancelled order cannot be updated
    with pytest.raises(grpc.aio.AioRpcError) as excinfo:
        await trader.client.update_gridpool_order(
            gridpool_id=GRIDPOOL_ID, order_id=order.order_id, price=trader.price
        )
    assert (
        excinfo.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    ), "Expected INVALID_ARGUMENT error"


@pytest.mark.skip(
    reason="Broken endpoint, see https://github.com/frequenz-floss/frequenz-client-electricity-trading-python/issues/162"
)
async def test_cancel_all_orders(trader: _TestTrader) -> None:
    """Test cancelling all orders."""
    # Create multiple orders
    for _ in range(10):
        await create_test_order(trader)

    # Cancel all orders and check that did indeed get cancelled
    await trader.client.cancel_all_gridpool_orders(GRIDPOOL_ID)

    orders = [
        order
        async for order in trader.client.list_gridpool_orders(
            gridpool_id=GRIDPOOL_ID,
        )
    ]

    for order in orders:
        assert (
            order.state_detail.state == OrderState.CANCELED
        ), f"Order {order.order_id} not canceled"


async def test_list_gridpool_trades(trader: _TestTrader) -> None:
    """Test listing gridpool trades."""
    buy_order, sell_order = await create_test_trade(trader)
    trades = [
        trade
        async for trade in trader.client.list_gridpool_trades(
            GRIDPOOL_ID,
            delivery_period=buy_order.order.delivery_period,
        )
    ]
    assert len(trades) >= 1


async def test_gridpool_orders_stream(trader: _TestTrader) -> None:
    """Test gridpool orders stream."""
    stream = trader.client.gridpool_orders_stream(GRIDPOOL_ID)
    receiver = stream.new_receiver()

    test_order = await create_test_order(trader)

    try:
        # Stream trades with a 15-second timeout to avoid indefinite hanging
        streamed_order = await asyncio.wait_for(anext(receiver), timeout=15)
        assert streamed_order is not None, "Failed to receive streamed order."
        assert (
            streamed_order.order == test_order.order
        ), "Streamed order does not match created order"
    except asyncio.TimeoutError:
        pytest.fail("Streaming timed out, no order received in 15 seconds")


async def test_receive_public_trades(trader: _TestTrader) -> None:
    """Test receive public trades."""
    stream = trader.client.receive_public_trades()
    receiver = stream.new_receiver()

    try:
        # Stream trades with a 15-second timeout to avoid indefinite hanging
        streamed_trade = await asyncio.wait_for(anext(receiver), timeout=15)
        assert streamed_trade is not None, "Failed to receive streamed trade"
    except asyncio.TimeoutError:
        pytest.fail("Streaming timed out, no trade received in 15 seconds")


async def test_receive_public_trades_filter(trader: _TestTrader) -> None:
    """Test receive public trades with filter set."""
    start_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start_time += timedelta(minutes=30 - start_time.minute % 15)  # next 15-minute mark

    delivery_period = DeliveryPeriod(start=start_time, duration=timedelta(minutes=15))

    price = Price(amount=Decimal("808"), currency=Currency.EUR)

    stream = trader.client.receive_public_trades(
        delivery_period=delivery_period,
    )
    receiver = stream.new_receiver()

    _ = await create_test_order(
        trader, delivery_period=delivery_period, side=MarketSide.BUY, price=price
    )
    _ = await create_test_order(
        trader, delivery_period=delivery_period, side=MarketSide.SELL, price=price
    )

    try:
        public_trade = await asyncio.wait_for(anext(receiver), timeout=15)
        assert public_trade, "Failed to receive public trade"
        assert public_trade.delivery_period.start == delivery_period.start
    except asyncio.TimeoutError:
        pytest.fail("Streaming timed out, no public trade received in 15 seconds")


async def test_gridpool_trades_stream(trader: _TestTrader) -> None:
    """Test gridpool trades stream."""
    stream = trader.client.gridpool_trades_stream(GRIDPOOL_ID)
    receiver = stream.new_receiver()

    # Create identical orders on opposite sides to try to trigger a trade
    await create_test_trade(trader)

    try:
        # Stream trades with a 15-second timeout to avoid indefinite hanging
        streamed_trade = await asyncio.wait_for(anext(receiver), timeout=15)
        assert streamed_trade is not None, "Failed to receive streamed trade"
    except asyncio.TimeoutError:
        pytest.fail("Streaming timed out, no trade received in 15 seconds")


async def test_create_order_zero_quantity(trader: _TestTrader) -> None:
    """Test creating an order with zero quantity."""
    zero_quantity = Power(mw=Decimal("0"))
    with pytest.raises(ValueError, match="Quantity must be strictly positive"):
        await create_test_order(trader, quantity=zero_quantity)


async def test_create_order_negative_quantity(trader: _TestTrader) -> None:
    """Test creating an order with a negative quantity."""
    negative_quantity = Power(mw=Decimal("-0.1"))
    with pytest.raises(ValueError, match="Quantity must be strictly positive"):
        await create_test_order(trader, quantity=negative_quantity)


async def test_create_order_maximum_price_precision_exceeded(
    trader: _TestTrader,
) -> None:
    """Test creating an order with excessive decimal precision in price."""
    excessive_precision_price = Price(amount=Decimal("56.123"), currency=Currency.EUR)
    with pytest.raises(ValueError, match="cannot have more than 2 decimal places"):
        await create_test_order(trader, price=excessive_precision_price)


async def test_create_order_maximum_quantity_precision_exceeded(
    trader: _TestTrader,
) -> None:
    """Test creating an order with excessive decimal precision in quantity."""
    excessive_precision_quantity = Power(mw=Decimal("0.5001"))
    with pytest.raises(
        ValueError, match="The quantity cannot have more than 1 decimal."
    ):
        await create_test_order(trader, quantity=excessive_precision_quantity)


async def test_cancel_non_existent_order(trader: _TestTrader) -> None:
    """Test canceling a non-existent order and expecting an error."""
    non_existent_order_id = 999999
    with pytest.raises(grpc.aio.AioRpcError) as excinfo:
        await trader.client.cancel_gridpool_order(
            GRIDPOOL_ID, order_id=non_existent_order_id
        )
    assert (
        excinfo.value.code() == grpc.StatusCode.UNAVAILABLE
    ), "Cancelling non-existent order should return an error"


async def test_cancel_already_cancelled_order(trader: _TestTrader) -> None:
    """Test cancelling an order twice to ensure idempotent behavior."""
    order = await create_test_order(trader)
    await trader.client.cancel_gridpool_order(GRIDPOOL_ID, order_id=order.order_id)
    with pytest.raises(grpc.aio.AioRpcError) as excinfo:
        cancelled_order = await trader.client.cancel_gridpool_order(
            GRIDPOOL_ID, order_id=order.order_id
        )
    assert (
        excinfo.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    ), "Order is already cancelled"


async def test_create_order_with_invalid_delivery_area(trader: _TestTrader) -> None:
    """Test creating an order with an invalid delivery area code."""
    invalid_delivery_area = DeliveryArea(
        code="INVALID_CODE", code_type=EnergyMarketCodeType.EUROPE_EIC
    )
    with pytest.raises(grpc.aio.AioRpcError) as excinfo:
        await trader.client.create_gridpool_order(
            gridpool_id=GRIDPOOL_ID,
            delivery_area=invalid_delivery_area,
            delivery_period=trader.delivery_period,
            order_type=trader.order_type,
            side=MarketSide.BUY,
            price=trader.price,
            quantity=trader.quantity,
            tag="invalid-delivery-area",
        )
    assert (
        excinfo.value.code() == grpc.StatusCode.UNAVAILABLE
    ), "Delivery area not found"


async def test_create_order_below_minimum_quantity(trader: _TestTrader) -> None:
    """Test creating an order with a quantity below the minimum allowed."""
    below_min_quantity = Power(mw=MIN_QUANTITY_MW - Decimal("0.01"))
    with pytest.raises(
        ValueError, match=f"Quantity must be at least {MIN_QUANTITY_MW} MW."
    ):
        await create_test_order(trader, quantity=below_min_quantity)


async def test_create_order_above_maximum_price(trader: _TestTrader) -> None:
    """Test creating an order with a price above the maximum allowed."""
    above_max_price = Price(amount=MAX_PRICE + Decimal("0.01"), currency=Currency.EUR)
    with pytest.raises(
        ValueError, match=f"Price must be between {MIN_PRICE} and {MAX_PRICE}."
    ):
        await create_test_order(trader, price=above_max_price)


async def test_create_order_at_maximum_price(trader: _TestTrader) -> None:
    """Test creating an order with the exact maximum allowed price."""
    max_price = Price(amount=MAX_PRICE, currency=Currency.EUR)
    order = await create_test_order(trader, price=max_price)
    assert (
        order.order.price.amount == max_price.amount
    ), "Order with maximum price was not created correctly"


async def test_create_order_at_minimum_quantity_and_price(
    trader: _TestTrader,
) -> None:
    """Test creating an order with the exact minimum allowed quantity and price."""
    min_quantity = Power(mw=MIN_QUANTITY_MW)
    min_price = Price(amount=MIN_PRICE, currency=Currency.EUR)
    order = await create_test_order(trader, quantity=min_quantity, price=min_price)
    assert (
        order.order.quantity.mw == min_quantity.mw
    ), "Order with minimum quantity was not created correctly"
    assert (
        order.order.price.amount == min_price.amount
    ), "Order with minimum price was not created correctly"


async def test_update_order_to_invalid_price(trader: _TestTrader) -> None:
    """Test updating an order to have a price outside the valid range."""
    order = await create_test_order(trader)
    invalid_price = Price(amount=MAX_PRICE + Decimal("0.01"), currency=Currency.EUR)
    with pytest.raises(
        ValueError, match=f"Price must be between {MIN_PRICE} and {MAX_PRICE}."
    ):
        await trader.client.update_gridpool_order(
            gridpool_id=GRIDPOOL_ID, order_id=order.order_id, price=invalid_price
        )


async def test_concurrent_cancel_and_update_order(trader: _TestTrader) -> None:
    """Test concurrent cancellation and update of the same order."""
    order = await create_test_order(trader)
    new_price = Price(amount=Decimal("50"), currency=Currency.EUR)

    cancelled_order = await trader.client.cancel_gridpool_order(
        GRIDPOOL_ID, order_id=order.order_id
    )

    with pytest.raises(grpc.aio.AioRpcError) as excinfo:
        await trader.client.update_gridpool_order(
            gridpool_id=GRIDPOOL_ID, order_id=order.order_id, price=new_price
        )
        assert (
            excinfo.value.code() == grpc.StatusCode.INVALID_ARGUMENT
        ), "Order is already cancelled"


async def test_multiple_streams_different_filters(trader: _TestTrader) -> None:
    """Test creating multiple streams with different filters and ensure independent operation."""
    area_1 = DeliveryArea(
        code="10YDE-EON------1", code_type=EnergyMarketCodeType.EUROPE_EIC
    )
    area_2 = DeliveryArea(
        code="10YDE-RWENET---I", code_type=EnergyMarketCodeType.EUROPE_EIC
    )

    stream_1 = trader.client.gridpool_orders_stream(GRIDPOOL_ID, delivery_area=area_1)
    receiver_1 = stream_1.new_receiver()

    stream_2 = trader.client.gridpool_orders_stream(GRIDPOOL_ID, delivery_area=area_2)
    receiver_2 = stream_2.new_receiver()

    # Create orders in each area to see if they appear on correct streams
    order_1 = await create_test_order(trader, delivery_area=area_1)
    order_2 = await create_test_order(trader, delivery_area=area_2)

    try:
        streamed_order_1 = await asyncio.wait_for(anext(receiver_1), timeout=15)
        streamed_order_2 = await asyncio.wait_for(anext(receiver_2), timeout=15)

        assert (
            streamed_order_1.order == order_1.order
        ), "Streamed order does not match area-specific order in stream 1"
        assert (
            streamed_order_2.order == order_2.order
        ), "Streamed order does not match area-specific order in stream 2"
    except asyncio.TimeoutError:
        pytest.fail("Failed to receive streamed orders within timeout")
