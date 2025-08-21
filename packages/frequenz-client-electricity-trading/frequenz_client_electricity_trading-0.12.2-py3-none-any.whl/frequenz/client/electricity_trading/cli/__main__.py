# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI tool to interact with the trading API."""

import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click

from frequenz.client.electricity_trading.cli.day_ahead import list_day_ahead_prices
from frequenz.client.electricity_trading.cli.etrading import (
    cancel_order as run_cancel_order,
)
from frequenz.client.electricity_trading.cli.etrading import (
    create_order as run_create_order,
)
from frequenz.client.electricity_trading.cli.etrading import (
    list_gridpool_orders as run_list_gridpool_orders,
)
from frequenz.client.electricity_trading.cli.etrading import (
    list_gridpool_trades as run_list_gridpool_trades,
)
from frequenz.client.electricity_trading.cli.etrading import (
    receive_public_orders as run_receive_public_orders,
)
from frequenz.client.electricity_trading.cli.etrading import (
    receive_public_trades as run_receive_public_trades,
)

TZ = ZoneInfo("Europe/Berlin")

iso = datetime.fromisoformat


def midnight(days: int = 0) -> str:
    """Return today's midnight."""
    return (
        datetime.combine(datetime.now(TZ), datetime.min.time(), tzinfo=TZ)
        + timedelta(days)
    ).isoformat()


@click.group()
def cli() -> None:
    """CLI tool to interact with the trading API."""


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", required=True, type=str)
@click.option("--delivery-start", default=None, type=iso)
@click.option("--start", default=None, type=iso)
@click.option("--end", default=None, type=iso)
@click.option("--sign_secret", default=None, type=str)
def receive_public_trades(  # pylint: disable=too-many-arguments
    url: str,
    auth_key: str,
    *,
    start: datetime,
    end: datetime,
    delivery_start: datetime,
    sign_secret: str | None = None,
) -> None:
    """List and/or stream public trades."""
    asyncio.run(
        run_receive_public_trades(
            url=url,
            auth_key=auth_key,
            delivery_start=delivery_start,
            start=start,
            end=end,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", required=True, type=str)
@click.option("--delivery-start", default=None, type=iso)
@click.option("--start", default=None, type=iso)
@click.option("--end", default=None, type=iso)
@click.option("--sign_secret", default=None, type=str)
def receive_public_orders(  # pylint: disable=too-many-arguments
    url: str,
    auth_key: str,
    *,
    start: datetime,
    end: datetime,
    delivery_start: datetime,
    sign_secret: str | None = None,
) -> None:
    """List and/or stream public trades."""
    asyncio.run(
        run_receive_public_orders(
            url=url,
            auth_key=auth_key,
            delivery_start=delivery_start,
            start=start,
            end=end,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", required=True, type=str)
@click.option("--gid", required=True, type=int)
@click.option("--start", default=None, type=iso)
@click.option("--sign_secret", default=None, type=str)
def receive_gridpool_trades(
    url: str,
    auth_key: str,
    gid: int,
    *,
    start: datetime,
    sign_secret: str | None = None,
) -> None:
    """List and/or stream gridpool trades."""
    asyncio.run(
        run_list_gridpool_trades(
            url=url,
            auth_key=auth_key,
            gid=gid,
            delivery_start=start,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", required=True, type=str)
@click.option("--start", default=None, type=iso)
@click.option("--gid", required=True, type=int)
@click.option("--sign_secret", default=None, type=str)
def receive_gridpool_orders(
    url: str,
    auth_key: str,
    *,
    start: datetime,
    gid: int,
    sign_secret: str | None = None,
) -> None:
    """List and/or stream gridpool orders."""
    asyncio.run(
        run_list_gridpool_orders(
            url=url,
            auth_key=auth_key,
            delivery_start=start,
            gid=gid,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", required=True, type=str)
@click.option("--start", required=True, type=iso)
@click.option("--gid", required=True, type=int)
@click.option("--quantity", required=True, type=str)
@click.option("--price", required=True, type=str)
@click.option("--area", required=True, type=str)
@click.option("--currency", default="EUR", type=str)
@click.option("--duration", default=900, type=int)
@click.option("--sign_secret", default=None, type=str)
def create_order(
    # pylint: disable=too-many-arguments
    url: str,
    auth_key: str,
    *,
    start: datetime,
    gid: int,
    quantity: str,
    price: str,
    area: str,
    currency: str,
    duration: int,
    sign_secret: str | None = None,
) -> None:
    """Create an order.

    This is only allowed in test instances.
    """
    if "test" not in url:
        raise ValueError("Creating orders is only allowed in test instances.")

    asyncio.run(
        run_create_order(
            url=url,
            auth_key=auth_key,
            delivery_start=start,
            gid=gid,
            quantity_mw=quantity,
            price=price,
            delivery_area=area,
            currency=currency,
            duration=timedelta(seconds=duration),
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", required=True, type=str)
@click.option("--gid", required=True, type=int)
@click.option("--order", required=True, type=int)
@click.option("--sign_secret", default=None, type=str)
def cancel_order(
    url: str, auth_key: str, gid: int, order: int, sign_secret: str | None = None
) -> None:
    """Cancel an order."""
    asyncio.run(
        run_cancel_order(
            url=url,
            auth_key=auth_key,
            gridpool_id=gid,
            order_id=order,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--url", required=True, type=str)
@click.option("--auth_key", required=True, type=str)
@click.option("--gid", required=True, type=int)
@click.option("--sign_secret", default=None, type=str)
def cancel_all_orders(
    url: str, auth_key: str, gid: int, sign_secret: str | None = None
) -> None:
    """Cancel all orders for a gridpool ID."""
    asyncio.run(
        run_cancel_order(
            url=url,
            auth_key=auth_key,
            gridpool_id=gid,
            order_id=None,
            sign_secret=sign_secret,
        )
    )


@cli.command()
@click.option("--entsoe-key", required=True, type=str)
@click.option("--start", default=midnight(), type=iso)
@click.option("--end", default=midnight(days=2), type=iso)
@click.option("--country-code", type=str, default="DE_LU")
def list_day_ahead(
    entsoe_key: str, *, start: datetime, end: datetime, country_code: str
) -> None:
    """List day-ahead prices."""
    list_day_ahead_prices(
        entsoe_key=entsoe_key, start=start, end=end, country_code=country_code
    )


def main() -> None:
    """Run the main Click CLI."""
    cli()


if __name__ == "__main__":
    main()
