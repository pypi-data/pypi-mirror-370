# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI tool to interact with the trading API."""

from collections import deque
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import AsyncIterator

from frequenz.client.electricity_trading import (
    Client,
    Currency,
    DeliveryArea,
    DeliveryPeriod,
    EnergyMarketCodeType,
    MarketSide,
    OrderDetail,
    OrderType,
    Power,
    Price,
    PublicOrder,
    PublicTrade,
    Trade,
)


def check_delivery_start(
    ts: datetime, duration: timedelta = timedelta(minutes=15)
) -> None:
    """Validate that the delivery start is a multiple of duration.

    Args:
        ts: Delivery start timestamp.
        duration: Delivery period duration.

    Raises:
        ValueError: If `ts` is not a multiple of `duration`.
    """
    if int(ts.timestamp()) % int(duration.total_seconds()) != 0:
        raise ValueError("Delivery period must be a multiple of `duration`.")


async def receive_public_trades(  # pylint: disable=too-many-arguments
    url: str,
    auth_key: str,
    *,
    delivery_start: datetime | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    sign_secret: str | None = None,
) -> None:
    """List trades and stream new public trades.

    Args:
        url: URL of the trading API.
        auth_key: API key.
        delivery_start: Start of the delivery period or None.
        start: First execution time to list trades from.
        end: Last execution time to list trades until.
        sign_secret: The cryptographic secret to use for HMAC generation.
    """
    client = Client(server_url=url, auth_key=auth_key, sign_secret=sign_secret)

    print_public_trade_header()

    delivery_period = None
    # If delivery period is selected, list historical trades also
    if delivery_start is not None:
        check_delivery_start(delivery_start)
        delivery_period = DeliveryPeriod(
            start=delivery_start,
            duration=timedelta(minutes=15),
        )
    stream = client.receive_public_trades(
        delivery_period=delivery_period,
        start_time=start,
        end_time=end,
    )
    async for trade in stream.new_receiver():
        print_public_trade(trade)


async def receive_public_orders(  # pylint: disable=too-many-arguments
    url: str,
    auth_key: str,
    *,
    delivery_start: datetime | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    sign_secret: str | None = None,
) -> None:
    """List trades and stream new public trades.

    Args:
        url: URL of the trading API.
        auth_key: API key.
        delivery_start: Start of the delivery period or None.
        start: First execution time to list trades from.
        end: Last execution time to list trades until.
        sign_secret: The cryptographic secret to use for HMAC generation.
    """
    client = Client(server_url=url, auth_key=auth_key, sign_secret=sign_secret)

    print_public_orders_header()

    delivery_period = None
    # If delivery period is selected, list historical trades also
    if delivery_start is not None:
        check_delivery_start(delivery_start)
        delivery_period = DeliveryPeriod(
            start=delivery_start,
            duration=timedelta(minutes=15),
        )
    stream = client.receive_public_order_book(
        delivery_period=delivery_period,
        start_time=start,
        end_time=end,
    )
    async for orders in stream.new_receiver():
        for order in orders:
            print_public_order(order)


async def list_gridpool_trades(
    url: str,
    auth_key: str,
    gid: int,
    *,
    delivery_start: datetime,
    sign_secret: str | None = None,
) -> None:
    """List gridpool trades and stream new gridpool trades.

    Optionally a delivery_start can be provided to filter the trades by delivery period.

    Args:
        url: URL of the trading API.
        auth_key: API key.
        gid: Gridpool ID.
        delivery_start: Start of the delivery period or None.
        sign_secret: The cryptographic secret to use for HMAC generation.
    """
    client = Client(server_url=url, auth_key=auth_key, sign_secret=sign_secret)

    print_trade_header()

    delivery_period = None
    # If delivery period is selected, list historical trades also
    if delivery_start is not None:
        check_delivery_start(delivery_start)
        delivery_period = DeliveryPeriod(
            start=delivery_start,
            duration=timedelta(minutes=15),
        )
    lst = client.list_gridpool_trades(gid, delivery_period=delivery_period)

    async for trade in lst:
        print_trade(trade)

    if delivery_start and delivery_start <= datetime.now(timezone.utc):
        return

    stream = client.gridpool_trades_stream(
        gid, delivery_period=delivery_period
    ).new_receiver()
    async for trade in stream:
        print_trade(trade)


async def list_gridpool_orders(
    url: str,
    auth_key: str,
    *,
    delivery_start: datetime,
    gid: int,
    sign_secret: str | None = None,
) -> None:
    """List orders and stream new gridpool orders.

    If delivery_start is provided, list historical orders and stream new orders
    for the 15 minute delivery period starting at delivery_start.
    If no delivery_start is provided, stream new orders for any delivery period.

    Note that retrieved sort order for listed orders (starting from the newest)
    is reversed in chunks trying to bring more recent orders to the bottom.

    Args:
        url: URL of the trading API.
        auth_key: API key.
        delivery_start: Start of the delivery period or None.
        gid: Gridpool ID.
        sign_secret: The cryptographic secret to use for HMAC generation.
    """
    client = Client(server_url=url, auth_key=auth_key, sign_secret=sign_secret)

    print_order_header()

    delivery_period = None
    # If delivery period is selected, list historical orders also
    if delivery_start is not None:
        check_delivery_start(delivery_start)
        delivery_period = DeliveryPeriod(
            start=delivery_start,
            duration=timedelta(minutes=15),
        )
    lst = client.list_gridpool_orders(gid, delivery_period=delivery_period)

    async for order in reverse_iterator(lst):
        print_order(order)

    if delivery_start and delivery_start <= datetime.now(timezone.utc):
        return

    stream = client.gridpool_orders_stream(
        gid, delivery_period=delivery_period
    ).new_receiver()
    async for order in stream:
        print_order(order)


# pylint: disable=too-many-arguments
async def create_order(
    url: str,
    auth_key: str,
    *,
    gid: int,
    delivery_start: datetime,
    delivery_area: str,
    price: str,
    quantity_mw: str,
    currency: str,
    duration: timedelta,
    sign_secret: str | None = None,
) -> None:
    """Create a limit order for a given price and quantity (in MW).

    The market side is determined by the sign of the quantity, positive for buy orders
    and negative for sell orders. The delivery area code is expected to be in
    EUROPE_EIC format.

    Args:
        url: URL of the trading API.
        auth_key: API key.
        gid: Gridpool ID.
        delivery_start: Start of the delivery period.
        delivery_area: Delivery area code.
        price: Price of the order.
        quantity_mw: Quantity in MW, positive for buy orders and negative for sell orders.
        currency: Currency of the price.
        duration: Duration of the delivery period.
        sign_secret: The cryptographic secret to use for HMAC generation.
    """
    client = Client(server_url=url, auth_key=auth_key, sign_secret=sign_secret)

    side = MarketSide.SELL if quantity_mw[0] == "-" else MarketSide.BUY
    quantity = Power(mw=Decimal(quantity_mw.lstrip("-")))
    check_delivery_start(delivery_start)
    order = await client.create_gridpool_order(
        gridpool_id=gid,
        delivery_area=DeliveryArea(
            code=delivery_area,
            code_type=EnergyMarketCodeType.EUROPE_EIC,
        ),
        delivery_period=DeliveryPeriod(
            start=delivery_start,
            duration=duration,
        ),
        order_type=OrderType.LIMIT,
        side=side,
        price=Price(
            amount=Decimal(price),
            currency=Currency[currency],
        ),
        quantity=quantity,
    )

    print_order(order)


async def cancel_order(
    url: str,
    auth_key: str,
    *,
    gridpool_id: int,
    order_id: int | None,
    sign_secret: str | None = None,
) -> None:
    """Cancel an order by order ID.

    If order_id is None, cancel all orders in the gridpool.

    Args:
        url: URL of the trading API.
        auth_key: API key.
        gridpool_id: Gridpool ID.
        order_id: Order ID to cancel or None to cancel all orders.
        sign_secret: The cryptographic secret to use for HMAC generation.
    """
    client = Client(server_url=url, auth_key=auth_key, sign_secret=sign_secret)
    if order_id is None:
        await client.cancel_all_gridpool_orders(gridpool_id)
    else:
        await client.cancel_gridpool_order(gridpool_id, order_id=order_id)


def print_public_trade_header() -> None:
    """Print trade header in CSV format."""
    header = (
        "public_trade_id,"
        "execution_time,"
        "delivery_period_start,"
        "delivery_period_duration,"
        "buy_delivery_area_code,"
        "sell_delivery_area_code,"
        "buy_delivery_area_code_type,"
        "sell_delivery_area_code_type,"
        "quantity_mw,"
        "currency,"
        "price,"
        "state "
    )
    print(header)


def print_public_trade(trade: PublicTrade) -> None:
    """Print trade details to stdout in CSV format."""
    values = (
        trade.public_trade_id,
        trade.execution_time.isoformat(),
        trade.delivery_period.start.isoformat(),
        trade.delivery_period.duration,
        trade.buy_delivery_area.code,
        trade.sell_delivery_area.code,
        trade.buy_delivery_area.code_type,
        trade.sell_delivery_area.code_type,
        trade.quantity.mw,
        trade.price.currency,
        trade.price.amount,
        trade.state,
    )
    print(",".join(v.name if isinstance(v, Enum) else str(v) for v in values))


def print_public_orders_header() -> None:
    """Print public order header in CSV format."""
    header = (
        "public_order_id,"
        "create_time,"
        "update_time,"
        "delivery_period_start,"
        "delivery_period_duration,"
        "delivery_area_code,"
        "quantity_mw,"
        "side,"
        "price_amount,"
        "price_currency,"
        "type,"
        "execution_option"
    )
    print(header)


def print_public_order(order: PublicOrder) -> None:
    """Print public order details to stdout in CSV format."""
    values = (
        order.public_order_id,
        order.create_time.isoformat(),
        order.update_time.isoformat(),
        order.delivery_period.start.isoformat(),
        order.delivery_period.duration,
        order.delivery_area.code,
        order.quantity.mw,
        order.side,
        order.price.amount,
        order.price.currency,
        order.type,
        order.execution_option,
    )
    print(",".join(v.name if isinstance(v, Enum) else str(v) for v in values))


def print_trade_header() -> None:
    """Print trade header in CSV format."""
    header = (
        "trade_id,"
        "order_id,"
        "execution_time,"
        "delivery_period_start,"
        "delivery_period_duration,"
        "delivery_area_code,"
        "delivery_area_code_type,"
        "side,"
        "quantity_mw,"
        "currency,"
        "price,"
        "state "
    )
    print(header)


def print_trade(trade: Trade) -> None:
    """Print trade details to stdout in CSV format."""
    values = (
        trade.id,
        trade.order_id,
        trade.execution_time.isoformat(),
        trade.delivery_period.start.isoformat(),
        trade.delivery_period.duration,
        trade.delivery_area.code,
        trade.delivery_area.code_type,
        trade.side,
        trade.quantity.mw,
        trade.price.currency,
        trade.price.amount,
        trade.state,
    )
    print(",".join(v.name if isinstance(v, Enum) else str(v) for v in values))


def print_order_header() -> None:
    """Print order header in CSV format."""
    header = (
        "order_id,"
        "create_time,"
        "modification_time,"
        "delivery_period_start,"
        "delivery_period_duration,"
        "delivery_area_code,"
        "delivery_area_code_type,"
        "order_type,"
        "quantity_mw,"
        "filled_quantity_mw,"
        "side,"
        "currency,"
        "price,"
        "state,"
        "tag"
    )
    print(header)


def print_order(order: OrderDetail) -> None:
    """
    Print order details to stdout in CSV format.

    All fields except the following are printed:
    - order.stop_price
    - order.peak_price_delta
    - order.display_quantity
    - order.execution_option
    - order.valid_until
    - order.payload
    - state_detail.state_reason
    - state_detail.market_actor
    - open_quantity

    Args:
        order: OrderDetail object
    """
    values = [
        order.order_id,
        order.create_time.isoformat(),
        order.modification_time.isoformat(),
        order.order.delivery_period.start.isoformat(),
        order.order.delivery_period.duration,
        order.order.delivery_area.code,
        order.order.delivery_area.code_type,
        order.order.type,
        order.order.quantity.mw,
        order.filled_quantity.mw,
        order.order.side,
        order.order.price.currency,
        order.order.price.amount,
        order.state_detail.state,
        order.order.tag,
    ]
    print(",".join(v.name if isinstance(v, Enum) else str(v) for v in values))


async def reverse_iterator(
    iterator: AsyncIterator[OrderDetail], chunk_size: int = 100_000
) -> AsyncIterator[OrderDetail]:
    """Reverse an async iterator in chunks to avoid loading all elements into memory.

    Args:
        iterator: Async iterator to reverse.
        chunk_size: Size of the buffer to store elements.

    Yields:
        Elements of the iterator in reverse order.
    """
    buffer: deque[OrderDetail] = deque(maxlen=chunk_size)
    async for item in iterator:
        buffer.append(item)
        if len(buffer) == chunk_size:
            for item in reversed(buffer):
                yield item
            buffer.clear()
    if buffer:
        for item in reversed(buffer):
            yield item
