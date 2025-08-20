"""Test simple REST API calls for submitting orders"""

import pytest
import time
import uuid
from decimal import Decimal
from typing import List
from uuid import UUID


def safe_round_price(price, tick_size):
    """Safely round price to tick_size using Decimal arithmetic to avoid floating-point precision issues."""
    price_decimal = Decimal(str(price))
    tick_size_decimal = Decimal(str(tick_size))
    return (price_decimal / tick_size_decimal).quantize(
        Decimal("1")
    ) * tick_size_decimal


def test_rest_limit_order_floats_submit_cancel(rc, sid):
    """Test submitting and cancelling a limit order with float inputs."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
    }
    order = rc.create_order(**order_params)
    rc.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc._models.SubmitOrderCreatedDto)

    # cancel the order
    cancelled_orders = rc.cancel_orders(
        sender=rc.chain.address, subaccount=subaccount.name, order_ids=[order.id]
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)


def test_rest_limit_order_decimal_submit_cancel(rc, sid):
    """Test submitting and cancelling a limit order with Decimal inputs."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    pid = rc.products_by_ticker["ETHUSD"].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    expires_at = int(time.time()) + 3600  # 1 hour from now
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": Decimal("1500.1"),
        "quantity": Decimal("4.1"),
        "time_in_force": "GTD",
        "expires_at": expires_at,
        "post_only": False,
    }
    order = rc.create_order(**order_params)
    rc.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc._models.SubmitOrderCreatedDto)

    # get the order and validate expires_at
    fetched_order = rc.get_order(order.id)
    assert isinstance(fetched_order, rc._models.OrderDto)
    assert fetched_order.id == order.id
    assert int(fetched_order.expires_at) == expires_at

    # cancel the order
    cancelled_orders = rc.cancel_orders(
        sender=rc.chain.address, subaccount=subaccount.name, order_ids=[order.id]
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)


def test_rest_limit_order_submit_cancel_multiple(rc, sid):
    """Test submitting and cancelling multiple limit orders."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
    }

    order_ids_to_cancel = []
    for i in range(2):
        order = rc.create_order(**order_params)
        rc.logger.info(f"Limit order: {order}")
        assert isinstance(order, rc._models.SubmitOrderCreatedDto)

        # append the order ID to the list of orders to cancel
        order_ids_to_cancel.append(order.id)

    # cancel the orders
    cancelled_orders = rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=order_ids_to_cancel,
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)


def test_rest_limit_order_submit_cancel_all(rc, sid):
    """Test submitting and cancelling several limit orders simultaneously."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id

    # start by cancelling all orders
    try:
        cancelled_orders = rc.cancel_all_orders(
            sender=rc.chain.address, subaccount_id=subaccount.id, product_ids=[pid]
        )
    except Exception as e:
        rc.logger.error(f"Error cancelling orders: {e}")

    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    order_ids = []
    for i in range(5):
        bid_price = best_bid_price * (0.90 + i * 0.01)
        bid_price = round(bid_price / tick_size) * tick_size
        order_params = {
            "order_type": "LIMIT",
            "product_id": pid,
            "side": 0,
            "price": bid_price,
            "quantity": 0.001,
        }
        order = rc.create_order(**order_params)
        assert isinstance(order, rc._models.SubmitOrderCreatedDto)

        order_ids.append(order.id)
    rc.logger.info(f"Order ids: {order_ids}")

    # cancel the orders
    cancelled_orders = rc.cancel_all_orders(
        sender=rc.chain.address, subaccount_id=subaccount.id, product_ids=[pid]
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert len(cancelled_orders) == len(order_ids)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)
    assert all([o.result.value == "Ok" for o in cancelled_orders])

    # check each of the orders
    # wait for the orders to be cancelled
    time.sleep(1)
    for order_id in order_ids:
        order = rc.get_order(id=order_id)
        assert isinstance(order, rc._models.OrderDto)
        assert order.status.value == "CANCELED"


def test_rest_limit_order_submit_cancel_all_specify_products(rc, sid):
    """Test submitting and cancelling several limit orders simultaneously.
    This test uses multiple products to test the order cancellation process."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    order_ids = {}
    for i in range(2):
        pid = rc.products[i].id
        tick_size = Decimal(str(rc.products_by_id[pid].tick_size))
        lot_size = Decimal(str(rc.products_by_id[pid].lot_size))
        prices = rc.list_market_prices(product_ids=[pid])[0]
        best_bid_price = Decimal(str(prices.best_bid_price))

        # bid 10% below the best bid price
        order_ids[pid] = []
        for j in range(5):
            bid_price = best_bid_price * Decimal(str(0.90 + j * 0.01))
            bid_price = safe_round_price(bid_price, tick_size)
            order_params = {
                "order_type": "LIMIT",
                "product_id": pid,
                "side": 0,
                "price": bid_price,
                "quantity": lot_size,
                "time_in_force": "GTD",
                "post_only": False,
            }
            order = rc.create_order(**order_params)
            assert isinstance(order, rc._models.SubmitOrderCreatedDto)
            order_ids[pid].append(order.id)

    rc.logger.info(f"Order ids: {order_ids}")

    # cancel the orders for product 1
    cancelled_orders = rc.cancel_all_orders(
        sender=rc.chain.address,
        subaccount_id=subaccount.id,
        product_ids=[rc.products[0].id],
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert len(cancelled_orders) == len(order_ids[rc.products[0].id])
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)
    assert all([o.result.value == "Ok" for o in cancelled_orders])

    # check each of the orders
    # wait for the orders to be cancelled
    time.sleep(1)
    for order_id in order_ids[rc.products[0].id]:
        order = rc.get_order(id=order_id)
        assert isinstance(order, rc._models.OrderDto)
        assert order.status.value == "CANCELED"

    for order_id in order_ids[rc.products[1].id]:
        order = rc.get_order(id=order_id)
        assert isinstance(order, rc._models.OrderDto)
        assert order.status.value == "NEW"

    # cancel the orders for product 2
    cancelled_orders = rc.cancel_all_orders(
        sender=rc.chain.address,
        subaccount_id=subaccount.id,
        product_ids=[rc.products[1].id],
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert len(cancelled_orders) == len(order_ids[rc.products[1].id])
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)
    assert all([o.result.value == "Ok" for o in cancelled_orders])

    # check each of the orders
    # wait for the orders to be cancelled
    time.sleep(1)
    for order_id in order_ids[rc.products[1].id]:
        order = rc.get_order(id=order_id)
        assert isinstance(order, rc._models.OrderDto)
        assert order.status.value == "CANCELED"


def test_rest_limit_order_submit_cancel_all_multiple_products(rc, sid):
    """Test submitting and cancelling several limit orders simultaneously.
    This test uses multiple products to test the order cancellation process
    across two products at once."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    order_ids = []
    for i in range(2):
        pid = rc.products[i].id
        tick_size = Decimal(str(rc.products_by_id[pid].tick_size))
        lot_size = Decimal(str(rc.products_by_id[pid].lot_size))
        prices = rc.list_market_prices(product_ids=[pid])[0]
        best_bid_price = Decimal(str(prices.best_bid_price))

        # bid 10% below the best bid price
        for j in range(5):
            bid_price = best_bid_price * Decimal(str(0.90 + j * 0.01))
            bid_price = safe_round_price(bid_price, tick_size)
            order_params = {
                "order_type": "LIMIT",
                "product_id": pid,
                "side": 0,
                "price": bid_price,
                "quantity": lot_size,
                "time_in_force": "GTD",
                "post_only": False,
            }
            order = rc.create_order(**order_params)
            assert isinstance(order, rc._models.SubmitOrderCreatedDto)

            order_ids.append(order.id)

    rc.logger.info(f"Order ids: {order_ids}")

    # cancel the orders
    cancelled_orders = rc.cancel_all_orders(
        sender=rc.chain.address,
        subaccount_id=subaccount.id,
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert len(cancelled_orders) == len(order_ids)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)
    assert all([o.result.value == "Ok" for o in cancelled_orders])

    # check each of the orders
    # wait for the orders to be cancelled
    time.sleep(1)
    for order_id in order_ids:
        order = rc.get_order(id=order_id)
        assert isinstance(order, rc._models.OrderDto)
        assert order.status.value == "CANCELED"


def test_rest_limit_order_dry(rc, sid):
    """Test dry running a limit order."""
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "dry_run": True,
    }
    order = rc.create_order(**order_params)
    rc.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc._models.DryRunOrderCreatedDto)


def test_rest_market_order_dry(rc, sid):
    """Test dry running a market order."""
    pid = rc.products[0].id
    order_params = {
        "order_type": "MARKET",
        "product_id": pid,
        "side": 0,
        "quantity": 0.001,
        "dry_run": True,
    }
    order = rc.create_order(**order_params)
    rc.logger.info(f"Market order: {order}")
    assert isinstance(order, rc._models.DryRunOrderCreatedDto)


def test_rest_market_order_submit(rc, sid):
    """Test submitting a market order."""
    pid = rc.products[0].id
    order_params = {
        "order_type": "MARKET",
        "product_id": pid,
        "side": 0,
        "quantity": 0.001,
    }
    order = rc.create_order(**order_params)
    rc.logger.info(f"Market order: {order}")
    assert isinstance(order, rc._models.SubmitOrderCreatedDto)


def test_rest_market_order_submit_close(rc, sid):
    """Test submitting a market order then a close order."""
    pid = rc.products[0].id
    order_1_params = {
        "order_type": "MARKET",
        "product_id": pid,
        "side": 0,
        "quantity": 0.001,
    }
    order_1 = rc.create_order(**order_1_params)
    rc.logger.info(f"Market order: {order_1}")
    assert isinstance(order_1, rc._models.SubmitOrderCreatedDto)

    # close the order
    order_2_params = {
        "order_type": "MARKET",
        "product_id": pid,
        "side": 1,
        "quantity": 0,
        "reduce_only": True,
        "close": True,
    }
    order_2 = rc.create_order(**order_2_params)
    rc.logger.info(f"Close order: {order_2}")
    assert isinstance(order_2, rc._models.SubmitOrderCreatedDto)


@pytest.mark.devnet_only
def test_rest_limit_order_with_stop(rc, sid):
    """Test submitting a limit order with stop parameters."""
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    stop_price = best_bid_price * 0.80
    stop_price = round(stop_price / tick_size) * tick_size

    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "stop_type": 1,
        "stop_price": stop_price,
    }
    order = rc.create_order(**order_params)
    rc.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc._models.SubmitOrderCreatedDto)


@pytest.mark.devnet_only
def test_rest_limit_order_with_otoco(rc, sid):
    """Test submitting a limit order with group parameters on devnet."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size

    # Use group_id and group_contingency_type parameters for devnet
    group_id = str(uuid.uuid4())
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "group_id": group_id,
        "group_contingency_type": 0,  # 0 = OTO (One Triggers Other)
    }
    order = rc.create_order(**order_params)
    rc.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc._models.SubmitOrderCreatedDto)
    # Order was successfully created with group parameters

    # cancel it
    cancelled_orders = rc.cancel_orders(
        sender=rc.chain.address, subaccount=subaccount.name, order_ids=[order.id]
    )
    assert isinstance(cancelled_orders, List)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)


@pytest.mark.devnet_only
def test_rest_limit_orders_with_otoco_group(rc, sid):
    """Test submitting limit orders with group parameters on devnet."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size

    # Generate a unique group ID for OTOCO
    group_id = str(uuid.uuid4())

    order_1_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "group_id": group_id,
        "group_contingency_type": 0,  # 0 = OTO
    }
    order_1 = rc.create_order(**order_1_params)
    rc.logger.info(f"Limit order: {order_1}")
    assert isinstance(order_1, rc._models.SubmitOrderCreatedDto)

    # Use the same group ID for the second order
    order_2_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "group_id": group_id,
        "group_contingency_type": 1,  # 1 = OCO with the first order
    }
    order_2 = rc.create_order(**order_2_params)
    rc.logger.info(f"Limit order: {order_2}")
    assert isinstance(order_2, rc._models.SubmitOrderCreatedDto)

    # cancel both
    cancelled_orders = rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[order_1.id, order_2.id],
    )
    assert isinstance(cancelled_orders, List)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)


def test_rest_market_order_submit_read_only(rc_ro, sid):
    """Test submitting a market order from a read-only client fails."""
    pid = rc_ro.products[0].id
    order_params = {
        "order_type": "MARKET",
        "product_id": pid,
        "side": 0,
        "quantity": 0.001,
    }

    with pytest.raises(Exception):
        rc_ro.create_order(**order_params)


def test_rest_limit_order_submit_replace_cancel(rc, sid):
    """Test submitting, replacing, and cancelling a limit order."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
    }
    order_result = rc.create_order(**order_params)
    rc.logger.info(f"Limit order: {order_result}")
    assert isinstance(order_result, rc._models.SubmitOrderCreatedDto)

    # check the original order
    time.sleep(1)
    order_before = rc.get_order(id=order_result.id)
    assert isinstance(order_before, rc._models.OrderDto)

    # replace the order
    new_price = float(order_before.price) * 1.01
    new_price = round(new_price / tick_size) * tick_size
    new_order, old_order_cancelled = rc.replace_order(
        order_id=order_before.id, price=new_price
    )
    rc.logger.info(f"Replaced order: {new_order}")
    assert isinstance(new_order, rc._models.SubmitOrderCreatedDto)
    assert isinstance(old_order_cancelled, bool)
    assert old_order_cancelled is True
    assert new_order.id != order_before.id

    # check the original order after
    time.sleep(1)
    order_after = rc.get_order(id=order_result.id)
    assert isinstance(order_after, rc._models.OrderDto)
    assert order_after.status.value == "CANCELED"

    # cancel the order
    cancelled_orders = rc.cancel_orders(
        sender=rc.chain.address, subaccount=subaccount.name, order_ids=[new_order.id]
    )
    rc.logger.info(f"Cancelled orders: {cancelled_orders}")
    assert isinstance(cancelled_orders, List)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)


def test_rest_prepare_limit_order(rc_ro, sid):
    """Test preparing a limit order."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    pid = rc_ro.products[0].id
    onchain_id = rc_ro.products[0].onchain_id
    tick_size = float(rc_ro.products_by_id[pid].tick_size)
    prices = rc_ro.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)


def test_rest_prepare_signed_limit_order(rc, sid):
    """Test preparing a limit order."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    onchain_id = rc.products[0].onchain_id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "sender": rc.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "include_signature": True,
    }
    order = rc.prepare_order(**order_params)
    rc.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc._models.SubmitOrderDto)
    assert order.signature != ""


def test_rest_prepare_market_order(rc_ro, sid):
    """Test preparing a market order."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "MARKET",
        "onchain_id": onchain_id,
        "side": 0,
        "price": "0",
        "quantity": 0.001,
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Market order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "MARKET"


def test_rest_create_order_with_float(rc_ro):
    """Test preparing an order with a float quantity input."""
    pid = rc_ro.products[0].id
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": 1000.1,
        "quantity": 4.1,
        "time_in_force": "GTD",
        "post_only": False,
        "sign": False,
        "submit": False,
    }
    order = rc_ro.create_order(**order_params)
    rc_ro.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "LIMIT"
    assert order.data.quantity == Decimal("4.1")


def test_rest_create_order_with_decimal(rc_ro, sid):
    """Test preparing an order with a decimal quantity input."""
    pid = rc_ro.products[0].id
    order_params = {
        "order_type": "LIMIT",
        "product_id": pid,
        "side": 0,
        "price": Decimal("1000.1"),
        "quantity": Decimal("4.1"),
        "time_in_force": "GTD",
        "post_only": False,
        "sign": False,
        "submit": False,
    }
    order = rc_ro.create_order(**order_params)
    rc_ro.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "LIMIT"
    assert order.data.quantity == Decimal("4.1")


def test_rest_create_order_with_string(rc_ro, sid):
    """Test preparing an order."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "MARKET",
        "onchain_id": onchain_id,
        "side": 0,
        "price": 0,
        "quantity": "4.1",
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Market order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "MARKET"
    assert order.data.quantity == Decimal("4.1")


def test_rest_prepare_market_order_with_float(rc_ro, sid):
    """Test preparing a market order with a float quantity input."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "MARKET",
        "onchain_id": onchain_id,
        "side": 0,
        "price": 0,
        "quantity": 4.1,
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Market order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "MARKET"
    assert order.data.quantity == Decimal("4.1")


def test_rest_prepare_market_order_with_decimal(rc_ro, sid):
    """Test preparing a market order with a decimal quantity input."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "MARKET",
        "onchain_id": onchain_id,
        "side": 0,
        "price": 0,
        "quantity": Decimal("4.1"),
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Market order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "MARKET"
    assert order.data.quantity == Decimal("4.1")


def test_rest_prepare_market_order_with_string(rc_ro, sid):
    """Test preparing a market order."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "MARKET",
        "onchain_id": onchain_id,
        "side": 0,
        "price": 0,
        "quantity": "4.1",
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Market order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "MARKET"
    assert order.data.quantity == Decimal("4.1")


def test_rest_prepare_limit_order_with_float(rc_ro, sid):
    """Test preparing a limit order using float inputs."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": 1001.1,
        "quantity": 4.1,
        "time_in_force": "GTD",
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "LIMIT"
    assert order.data.price == Decimal("1001.1")
    assert order.data.quantity == Decimal("4.1")


def test_rest_prepare_limit_order_with_string(rc_ro, sid):
    """Test preparing a limit order using string inputs."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": "1001.1",
        "quantity": "4.1",
        "time_in_force": "GTD",
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "LIMIT"
    assert order.data.price == Decimal("1001.1")
    assert order.data.quantity == Decimal("4.1")


def test_rest_prepare_limit_order_with_decimal(rc_ro, sid):
    """Test preparing a limit order using decimal inputs."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": Decimal("1001.1"),
        "quantity": Decimal("4.1"),
        "time_in_force": "GTD",
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.type.value == "LIMIT"
    assert order.data.price == Decimal("1001.1")
    assert order.data.quantity == Decimal("4.1")


def test_rest_prepare_and_sign_limit_order(rc, sid):
    """Test preparing and signing a limit order."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    onchain_id = rc.products[0].onchain_id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "sender": rc.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "include_signature": True,
    }
    order = rc.prepare_order(**order_params)
    rc.logger.info(f"Signed limit order: {order}")
    assert isinstance(order, rc._models.SubmitOrderDto)
    assert order.signature != ""


def test_rest_prepare_and_sign_market_order(rc, sid):
    """Test preparing and signing a market order."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    onchain_id = rc.products[0].onchain_id
    order_params = {
        "sender": rc.chain.address,
        "subaccount": subaccount.name,
        "order_type": "MARKET",
        "onchain_id": onchain_id,
        "side": 0,
        "price": "0",
        "quantity": 0.001,
        "include_signature": True,
    }
    order = rc.prepare_order(**order_params)
    rc.logger.info(f"Signed market order: {order}")
    assert isinstance(order, rc._models.SubmitOrderDto)
    assert order.data.type.value == "MARKET"
    assert order.signature != ""


def test_rest_prepare_sign_submit_limit_order(rc, sid):
    """Test preparing, signing, and submitting a limit order."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    onchain_id = rc.products[0].onchain_id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "sender": rc.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "include_signature": True,
    }
    prepared_order = rc.prepare_order(**order_params)
    assert isinstance(prepared_order, rc._models.SubmitOrderDto)
    assert prepared_order.signature != ""

    # Submit the prepared order
    submitted_order = rc.submit_order(prepared_order)
    rc.logger.info(f"Submitted order: {submitted_order}")
    assert isinstance(submitted_order, rc._models.SubmitOrderCreatedDto)

    # Clean up - cancel the order
    cancelled_orders = rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[submitted_order.id],
    )
    assert isinstance(cancelled_orders, List)
    assert all(isinstance(o, rc._models.CancelOrderResultDto) for o in cancelled_orders)


def test_rest_prepare_dry_run_limit_order(rc_ro, sid):
    """Test preparing and dry running a limit order."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    pid = rc_ro.products[0].id
    onchain_id = rc_ro.products[0].onchain_id
    tick_size = float(rc_ro.products_by_id[pid].tick_size)
    prices = rc_ro.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
    }
    prepared_order = rc_ro.prepare_order(**order_params)
    assert isinstance(prepared_order, rc_ro._models.SubmitOrderDto)

    # Dry run the order
    dry_run_result = rc_ro.dry_run_order(prepared_order)
    rc_ro.logger.info(f"Dry run result: {dry_run_result}")
    assert isinstance(dry_run_result, rc_ro._models.DryRunOrderCreatedDto)


def test_rest_prepare_cancel_order(rc_ro, sid):
    """Test preparing cancel order parameters."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]

    # Create mock order IDs to cancel
    order_ids_to_cancel = [
        UUID("c88a748b-67bc-4ed0-8442-eebceb501c77"),
        UUID("724f7376-cc80-4ecd-8a89-da80cdb7310a"),
    ]

    cancel_params = {
        "order_ids": order_ids_to_cancel,
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
    }
    cancel_order = rc_ro.prepare_cancel_order(**cancel_params)
    rc_ro.logger.info(f"Cancel order preparation: {cancel_order}")
    assert isinstance(cancel_order, rc_ro._models.CancelOrderDto)
    assert cancel_order.data.order_ids == order_ids_to_cancel


def test_rest_prepare_sign_cancel_order(rc, sid):
    """Test preparing and signing cancel order parameters."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    # Create mock order IDs to cancel
    order_ids_to_cancel = [
        "c88a748b-67bc-4ed0-8442-eebceb501c77",
        "724f7376-cc80-4ecd-8a89-da80cdb7310a",
    ]

    cancel_params = {
        "order_ids": order_ids_to_cancel,
        "sender": rc.chain.address,
        "subaccount": subaccount.name,
        "include_signature": True,
    }
    cancel_order = rc.prepare_cancel_order(**cancel_params)
    rc.logger.info(f"Signed cancel order: {cancel_order}")
    assert isinstance(cancel_order, rc._models.CancelOrderDto)
    assert cancel_order.signature != ""


def test_rest_prepare_limit_order_with_stop(rc_ro, sid):
    """Test preparing a limit order with stop parameters."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    pid = rc_ro.products[0].id
    onchain_id = rc_ro.products[0].onchain_id
    tick_size = float(rc_ro.products_by_id[pid].tick_size)
    prices = rc_ro.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size
    stop_price = best_bid_price * 0.80
    stop_price = round(stop_price / tick_size) * tick_size

    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "stop_price": stop_price,
        "stop_type": 1,
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Stop limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.stop_price == stop_price
    assert order.data.stop_type.value == 1


def test_rest_prepare_limit_order_with_reduce_only(rc_ro, sid):
    """Test preparing a limit order with reduce only flag."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    pid = rc_ro.products[0].id
    onchain_id = rc_ro.products[0].onchain_id
    tick_size = float(rc_ro.products_by_id[pid].tick_size)
    prices = rc_ro.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    # bid 10% below the best bid price
    bid_price = best_bid_price * 0.90
    bid_price = round(bid_price / tick_size) * tick_size

    order_params = {
        "sender": rc_ro.chain.address,
        "subaccount": subaccount.name,
        "order_type": "LIMIT",
        "onchain_id": onchain_id,
        "side": 0,
        "price": bid_price,
        "quantity": 0.001,
        "time_in_force": "GTD",
        "post_only": False,
        "reduce_only": True,
    }
    order = rc_ro.prepare_order(**order_params)
    rc_ro.logger.info(f"Reduce only limit order: {order}")
    assert isinstance(order, rc_ro._models.SubmitOrderDto)
    assert order.data.reduce_only
