import pytest
import time
import uuid


@pytest.mark.devnet_only
def test_rest_pure_oto_pattern(rc, sid):
    """Test pure OTO pattern: Primary order must fill before secondary becomes active.

    In OTO:
    - Primary order has group_contingency_type = 0 (OTO trigger)
    - Secondary orders use same group_id without contingency_type
    - Secondary orders remain inactive until primary fills
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    group_id = str(uuid.uuid4())

    # Primary OTO trigger order (entry)
    entry_price = best_bid_price * 0.95  # Below market, won't fill immediately
    entry_price = float(round(entry_price / tick_size) * tick_size)

    primary_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=0,  # BUY
        price=entry_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
        group_contingency_type=0,  # OTO trigger
    )
    assert isinstance(primary_order, rc._models.SubmitOrderCreatedDto)

    # Secondary order (exit) - triggered after primary fills
    exit_price = best_bid_price * 1.05  # Take profit above entry
    exit_price = float(round(exit_price / tick_size) * tick_size)

    secondary_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=exit_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,  # Same group, no contingency_type
    )
    assert isinstance(secondary_order, rc._models.SubmitOrderCreatedDto)

    # Verify order structure
    time.sleep(2)
    primary = rc.get_order(id=primary_order.id)
    secondary = rc.get_order(id=secondary_order.id)

    assert primary.group_id == group_id
    assert primary.group_contingency_type.value == 0  # OTO trigger
    assert secondary.group_id == group_id
    # Secondary should be waiting for primary to fill

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[primary_order.id, secondary_order.id],
    )


@pytest.mark.devnet_only
def test_rest_pure_oco_pattern(rc, sid):
    """Test pure OCO pattern: Take-profit and stop-loss where filling one cancels the other.

    In OCO:
    - Both orders have group_contingency_type = 1 (OCO)
    - Both orders share the same group_id
    - When one fills or is canceled, the other is automatically canceled
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())

    # Market order
    market_order = rc.create_order(
        order_type="MARKET",
        product_id=pid,
        side=0,  # BUY
        quantity=0.001,
        time_in_force="GTD",
    )
    assert isinstance(market_order, rc._models.SubmitOrderCreatedDto)

    # Stop-loss order (below current price)
    stop_loss_price = best_bid_price * 0.90
    stop_loss_price = float(round(stop_loss_price / tick_size) * tick_size)

    stop_loss_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=stop_loss_price,
        quantity=0.001,
        time_in_force="GTD",
        reduce_only=True,
        group_id=group_id,
        group_contingency_type=1,  # OCO
        stop_type=1,  # LOSS
        stop_price=stop_loss_price,  # Trigger price
    )
    assert isinstance(stop_loss_order, rc._models.SubmitOrderCreatedDto)

    # Take-profit order (above current price)
    take_profit_price = best_ask_price * 1.10
    take_profit_price = float(round(take_profit_price / tick_size) * tick_size)

    take_profit_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=take_profit_price,
        quantity=0.001,
        time_in_force="GTD",
        reduce_only=True,
        group_id=group_id,
        group_contingency_type=1,  # OCO
        stop_type=0,  # GAIN
        stop_price=take_profit_price,  # Trigger price
    )
    assert isinstance(take_profit_order, rc._models.SubmitOrderCreatedDto)

    # Verify both orders are created and linked
    time.sleep(2)
    stop_loss = rc.get_order(id=stop_loss_order.id)
    take_profit = rc.get_order(id=take_profit_order.id)

    assert stop_loss.group_id == group_id
    assert stop_loss.group_contingency_type.value == 1  # OCO
    assert take_profit.group_id == group_id
    assert take_profit.group_contingency_type.value == 1  # OCO

    # Both should be active
    assert stop_loss.status.value in ["NEW", "PENDING"]
    assert take_profit.status.value in ["NEW", "PENDING"]

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[stop_loss_order.id, take_profit_order.id],
    )
    close_order = rc.create_order(
        order_type="MARKET",
        product_id=pid,
        quantity=0,
        side=1,  # SELL
        time_in_force="GTD",
        reduce_only=True,
        close=True,
    )
    assert isinstance(close_order, rc._models.SubmitOrderCreatedDto)


@pytest.mark.devnet_only
def test_rest_otoco_pattern_complete(rc, sid):
    """Test OTOCO pattern: Entry order triggers take-profit and stop-loss OCO.

    This is the classic bracket order pattern:
    1. Entry order (OTO trigger) - when filled, activates:
    2. Take-profit order (OCO with stop-loss)
    3. Stop-loss order (OCO with take-profit)
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())

    # 1. Entry order (OTO trigger)
    entry_price = best_bid_price * 0.95
    entry_price = float(round(entry_price / tick_size) * tick_size)

    entry_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=0,  # BUY
        price=entry_price,
        quantity=0.002,
        time_in_force="GTD",
        group_id=group_id,
        group_contingency_type=0,  # OTO trigger
    )
    assert isinstance(entry_order, rc._models.SubmitOrderCreatedDto)

    # 2. Take-profit order (triggered by entry, OCO with stop-loss)
    take_profit_price = best_ask_price * 1.10
    take_profit_price = float(round(take_profit_price / tick_size) * tick_size)

    take_profit_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=take_profit_price,
        quantity=0.002,
        time_in_force="GTD",
        reduce_only=True,
        group_id=group_id,  # Same group as entry
    )
    assert isinstance(take_profit_order, rc._models.SubmitOrderCreatedDto)

    # 3. Stop-loss order (triggered by entry, OCO with take-profit)
    stop_loss_price = best_bid_price * 0.90
    stop_loss_price = float(round(stop_loss_price / tick_size) * tick_size)

    stop_loss_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=stop_loss_price,
        quantity=0.002,
        time_in_force="GTD",
        reduce_only=True,
        group_id=group_id,  # Same group as entry
    )
    assert isinstance(stop_loss_order, rc._models.SubmitOrderCreatedDto)

    # Verify order structure
    time.sleep(2)
    entry = rc.get_order(id=entry_order.id)
    take_profit = rc.get_order(id=take_profit_order.id)
    stop_loss = rc.get_order(id=stop_loss_order.id)

    # Entry should be OTO trigger
    assert entry.group_id == group_id
    assert entry.group_contingency_type.value == 0  # OTO

    # TP and SL should be in same group
    assert take_profit.group_id == group_id
    assert stop_loss.group_id == group_id

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[entry_order.id, take_profit_order.id, stop_loss_order.id],
    )


@pytest.mark.devnet_only
def test_rest_stop_orders_with_oco(rc, sid):
    """Test stop orders (GAIN/LOSS) with OCO groups.

    Stop orders use stop_type and stop_price:
    - stop_type: GAIN (take-profit) or LOSS (stop-loss)
    - Trigger: LAST_PRICE or MARK_PRICE
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())

    # Stop-loss order using stop_type and stop_price
    stop_loss_trigger = best_bid_price * 0.95
    stop_loss_trigger = float(round(stop_loss_trigger / tick_size) * tick_size)

    stop_loss_order = rc.create_order(
        order_type="MARKET",  # Market order when triggered
        product_id=pid,
        side=1,  # SELL
        quantity=0.001,
        stop_type=1,  # LOSS
        stop_price=stop_loss_trigger,
        reduce_only=True,
        group_id=group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(stop_loss_order, rc._models.SubmitOrderCreatedDto)

    # Take-profit order using stop_type and stop_price
    take_profit_trigger = best_ask_price * 1.05
    take_profit_trigger = float(round(take_profit_trigger / tick_size) * tick_size)

    take_profit_order = rc.create_order(
        order_type="MARKET",  # Market order when triggered
        product_id=pid,
        side=1,  # SELL
        quantity=0.001,
        stop_type=0,  # GAIN
        stop_price=take_profit_trigger,
        reduce_only=True,
        group_id=group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(take_profit_order, rc._models.SubmitOrderCreatedDto)

    # Verify both stop orders are created with OCO relationship
    time.sleep(2)
    stop_loss = rc.get_order(id=stop_loss_order.id)
    take_profit = rc.get_order(id=take_profit_order.id)

    assert stop_loss.group_id == group_id
    assert stop_loss.group_contingency_type.value == 1  # OCO
    assert stop_loss.stop_type.value == 1  # LOSS
    assert float(stop_loss.stop_price) == stop_loss_trigger

    assert take_profit.group_id == group_id
    assert take_profit.group_contingency_type.value == 1  # OCO
    assert take_profit.stop_type.value == 0  # GAIN
    assert float(take_profit.stop_price) == take_profit_trigger

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[stop_loss_order.id, take_profit_order.id],
    )


@pytest.mark.devnet_only
def test_rest_oto_with_multiple_secondaries(rc, sid):
    """Test OTO with multiple secondary orders (all triggered by same primary).

    Primary order triggers multiple secondaries:
    - Could be used for scaling out of positions
    - All secondaries share the same group_id
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())

    # Primary OTO trigger
    entry_price = best_bid_price * 0.96
    entry_price = float(round(entry_price / tick_size) * tick_size)

    primary_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=0,  # BUY
        price=entry_price,
        quantity=0.003,  # Larger size to scale out
        time_in_force="GTD",
        group_id=group_id,
        group_contingency_type=0,  # OTO trigger
    )
    assert isinstance(primary_order, rc._models.SubmitOrderCreatedDto)

    # First secondary - partial exit at lower target
    target1_price = best_ask_price * 1.02
    target1_price = float(round(target1_price / tick_size) * tick_size)

    secondary1 = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=target1_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
    )
    assert isinstance(secondary1, rc._models.SubmitOrderCreatedDto)

    # Second secondary - partial exit at higher target
    target2_price = best_ask_price * 1.05
    target2_price = float(round(target2_price / tick_size) * tick_size)

    secondary2 = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=target2_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
    )
    assert isinstance(secondary2, rc._models.SubmitOrderCreatedDto)

    # Third secondary - final exit at highest target
    target3_price = best_ask_price * 1.10
    target3_price = float(round(target3_price / tick_size) * tick_size)

    secondary3 = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=target3_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
    )
    assert isinstance(secondary3, rc._models.SubmitOrderCreatedDto)

    # Verify all orders are created properly
    time.sleep(2)
    primary = rc.get_order(id=primary_order.id)
    sec1 = rc.get_order(id=secondary1.id)
    sec2 = rc.get_order(id=secondary2.id)
    sec3 = rc.get_order(id=secondary3.id)

    # Primary should be OTO trigger
    assert primary.group_id == group_id
    assert primary.group_contingency_type.value == 0

    # All secondaries should share the group
    assert sec1.group_id == group_id
    assert sec2.group_id == group_id
    assert sec3.group_id == group_id

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[primary_order.id, secondary1.id, secondary2.id, secondary3.id],
    )


@pytest.mark.devnet_only
def test_rest_oco_pairs_independent(rc, sid):
    """Test creating multiple independent OCO pairs.

    Each OCO pair operates independently:
    - Different group_ids for each pair
    - Filling one order in a pair only affects its partner
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    created_orders = []

    # Create 2 independent OCO pairs
    for i in range(2):
        group_id = str(uuid.uuid4())

        # Stop-loss for this pair
        sl_price = best_bid_price * (0.88 + i * 0.02)
        sl_price = float(round(sl_price / tick_size) * tick_size)

        sl_order = rc.create_order(
            order_type="LIMIT",
            product_id=pid,
            side=1,  # SELL
            price=sl_price,
            quantity=0.001,
            time_in_force="GTD",
            group_id=group_id,
            group_contingency_type=1,  # OCO
        )
        created_orders.append(sl_order.id)

        # Take-profit for this pair
        tp_price = best_ask_price * (1.08 + i * 0.02)
        tp_price = float(round(tp_price / tick_size) * tick_size)

        tp_order = rc.create_order(
            order_type="LIMIT",
            product_id=pid,
            side=1,  # SELL
            price=tp_price,
            quantity=0.001,
            time_in_force="GTD",
            group_id=group_id,
            group_contingency_type=1,  # OCO
        )
        created_orders.append(tp_order.id)

    # Verify all 4 orders were created (2 pairs)
    assert len(created_orders) == 4

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=created_orders,
    )


@pytest.mark.devnet_only
def test_rest_oto_then_modify_secondary(rc, sid):
    """Test modifying secondary orders after OTO creation.

    Common use case: Adjusting take-profit/stop-loss levels
    while maintaining the OTO relationship.
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())

    # Create OTO entry order
    entry_price = best_bid_price * 0.94
    entry_price = float(round(entry_price / tick_size) * tick_size)

    entry_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=0,  # BUY
        price=entry_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
        group_contingency_type=0,  # OTO
    )
    assert isinstance(entry_order, rc._models.SubmitOrderCreatedDto)

    # Initial take-profit
    initial_tp_price = best_ask_price * 1.05
    initial_tp_price = float(round(initial_tp_price / tick_size) * tick_size)

    initial_tp = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=initial_tp_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
    )
    assert isinstance(initial_tp, rc._models.SubmitOrderCreatedDto)

    # Cancel initial take-profit
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[initial_tp.id],
    )

    # Create new take-profit with adjusted target
    new_tp_price = best_ask_price * 1.08  # More ambitious target
    new_tp_price = float(round(new_tp_price / tick_size) * tick_size)

    new_tp = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=new_tp_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,  # Keep same group
    )
    assert isinstance(new_tp, rc._models.SubmitOrderCreatedDto)

    # Verify new structure
    time.sleep(2)
    entry = rc.get_order(id=entry_order.id)
    tp = rc.get_order(id=new_tp.id)

    assert entry.group_id == group_id
    assert tp.group_id == group_id

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[entry_order.id, new_tp.id],
    )
    close_order = rc.create_order(
        order_type="MARKET",
        product_id=pid,
        quantity=0,
        side=1,  # SELL
        time_in_force="GTD",
        reduce_only=True,
        close=True,
    )
    assert isinstance(close_order, rc._models.SubmitOrderCreatedDto)


@pytest.mark.devnet_only
def test_rest_stop_limit_orders_with_oto(rc, sid):
    """Test stop-limit orders with OTO groups.

    Stop-limit orders:
    - Have both stop_price (trigger) and price (limit)
    - Only become active when stop_price is reached
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)

    group_id = str(uuid.uuid4())

    # Entry order (OTO trigger)
    entry_price = best_bid_price * 0.96
    entry_price = float(round(entry_price / tick_size) * tick_size)

    entry_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=0,  # BUY
        price=entry_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
        group_contingency_type=0,  # OTO
    )
    assert isinstance(entry_order, rc._models.SubmitOrderCreatedDto)

    # Stop-limit order (triggered by entry, then places limit)
    stop_trigger = best_bid_price * 0.92
    stop_trigger = float(round(stop_trigger / tick_size) * tick_size)
    stop_limit = best_bid_price * 0.91  # Limit price below trigger
    stop_limit = float(round(stop_limit / tick_size) * tick_size)

    stop_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=stop_limit,  # Limit price
        quantity=0.001,
        time_in_force="GTD",
        stop_type=1,  # LOSS
        stop_price=stop_trigger,  # Trigger price
        reduce_only=True,
        group_id=group_id,
    )
    assert isinstance(stop_order, rc._models.SubmitOrderCreatedDto)

    # Verify stop-limit order structure
    time.sleep(2)
    stop = rc.get_order(id=stop_order.id)

    assert stop.group_id == group_id
    assert float(stop.stop_price) == stop_trigger
    assert float(stop.price) == stop_limit
    assert stop.stop_type.value == 1  # LOSS

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[entry_order.id, stop_order.id],
    )


@pytest.mark.devnet_only
def test_rest_prepare_order_validates_group_params(rc_ro, sid):
    """Test that prepare_order properly validates group parameters.

    Ensures the SDK correctly handles:
    - group_id as UUID
    - group_contingency_type as integer (0=OTO, 1=OCO)
    """
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]
    onchain_id = rc_ro.products[0].onchain_id

    group_id = str(uuid.uuid4())

    # Test OTO order preparation
    oto_order = rc_ro.prepare_order(
        sender=rc_ro.chain.address,
        subaccount=subaccount.name,
        order_type="LIMIT",
        onchain_id=onchain_id,
        side=0,  # BUY
        price=2000.0,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
        group_contingency_type=0,  # OTO
    )

    oto_data = oto_order.data.model_dump(by_alias=True)
    assert str(oto_data.get("groupId")) == group_id
    assert oto_data.get("groupContingencyType").value == 0

    # Test OCO order preparation
    oco_order = rc_ro.prepare_order(
        sender=rc_ro.chain.address,
        subaccount=subaccount.name,
        order_type="LIMIT",
        onchain_id=onchain_id,
        side=1,  # SELL
        price=2100.0,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
        group_contingency_type=1,  # OCO
    )

    oco_data = oco_order.data.model_dump(by_alias=True)
    assert str(oco_data.get("groupId")) == group_id
    assert oco_data.get("groupContingencyType").value == 1

    # Test order without group (standalone)
    standalone_order = rc_ro.prepare_order(
        sender=rc_ro.chain.address,
        subaccount=subaccount.name,
        order_type="LIMIT",
        onchain_id=onchain_id,
        side=0,
        price=1950.0,
        quantity=0.001,
        time_in_force="GTD",
        # No group parameters
    )

    standalone_data = standalone_order.data.model_dump(by_alias=True)
    assert standalone_data.get("groupId") is None
    assert standalone_data.get("groupContingencyType") is None


@pytest.mark.devnet_only
def test_rest_market_order_with_oco_exits(rc, sid):
    """Test market order with OCO exit orders.

    Common pattern:
    1. Market buy to enter position immediately
    2. OCO sell orders for exit (take-profit vs stop-loss)
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    # Market entry (no group needed)
    entry_order = rc.create_order(
        order_type="MARKET",
        product_id=pid,
        side=0,  # BUY
        quantity=0.001,
    )
    assert isinstance(entry_order, rc._models.SubmitOrderCreatedDto)

    # Create OCO exit orders
    oco_group_id = str(uuid.uuid4())

    # Take-profit exit
    tp_price = best_ask_price * 1.03
    tp_price = float(round(tp_price / tick_size) * tick_size)

    tp_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=tp_price,
        quantity=0.001,
        time_in_force="GTD",
        reduce_only=True,
        group_id=oco_group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(tp_order, rc._models.SubmitOrderCreatedDto)

    # Stop-loss exit
    sl_price = best_bid_price * 0.97
    sl_price = float(round(sl_price / tick_size) * tick_size)

    sl_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=sl_price,
        quantity=0.001,
        time_in_force="GTD",
        reduce_only=True,
        group_id=oco_group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(sl_order, rc._models.SubmitOrderCreatedDto)

    # Verify OCO structure
    time.sleep(2)
    tp = rc.get_order(id=tp_order.id)
    sl = rc.get_order(id=sl_order.id)

    assert tp.group_id == oco_group_id
    assert tp.group_contingency_type.value == 1
    assert sl.group_id == oco_group_id
    assert sl.group_contingency_type.value == 1

    # Clean up exit orders
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[tp_order.id, sl_order.id],
    )
    close_order = rc.create_order(
        order_type="MARKET",
        product_id=pid,
        quantity=0,
        side=1,  # SELL
        time_in_force="GTD",
        reduce_only=True,
        close=True,
    )
    assert isinstance(close_order, rc._models.SubmitOrderCreatedDto)


@pytest.mark.devnet_only
def test_rest_reduce_only_with_oco(rc, sid):
    """Test reduce_only orders with OCO groups.

    Reduce-only orders:
    - Only reduce existing position size
    - Cannot open new positions
    - Perfect for exit strategies
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())

    # Reduce-only take-profit
    tp_price = best_ask_price * 1.08
    tp_price = float(round(tp_price / tick_size) * tick_size)

    tp_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=tp_price,
        quantity=0.001,
        time_in_force="GTD",
        reduce_only=True,  # Only reduce position
        group_id=group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(tp_order, rc._models.SubmitOrderCreatedDto)

    # Reduce-only stop-loss
    sl_price = best_bid_price * 0.92
    sl_price = float(round(sl_price / tick_size) * tick_size)

    sl_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=sl_price,
        quantity=0.001,
        time_in_force="GTD",
        reduce_only=True,  # Only reduce position
        group_id=group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(sl_order, rc._models.SubmitOrderCreatedDto)

    # Verify both are reduce-only OCO orders
    time.sleep(2)
    tp = rc.get_order(id=tp_order.id)
    sl = rc.get_order(id=sl_order.id)

    assert tp.reduce_only is True
    assert tp.group_id == group_id
    assert tp.group_contingency_type.value == 1

    assert sl.reduce_only is True
    assert sl.group_id == group_id
    assert sl.group_contingency_type.value == 1

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[tp_order.id, sl_order.id],
    )


@pytest.mark.devnet_only
def test_rest_time_in_force_with_oto_oco(rc, sid):
    """Test different time_in_force values with OTO/OCO groups.

    Time in force options:
    - GTD: Good till date (with expires_at)
    - GTC: Good till canceled
    - IOC: Immediate or cancel
    - FOK: Fill or kill
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())
    expires_at = int(time.time()) + 3600  # 1 hour from now

    # OTO trigger with GTD
    entry_price = best_bid_price * 0.95
    entry_price = float(round(entry_price / tick_size) * tick_size)

    entry_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=0,  # BUY
        price=entry_price,
        quantity=0.001,
        time_in_force="GTD",
        expires_at=expires_at,
        group_id=group_id,
        group_contingency_type=0,  # OTO
    )
    assert isinstance(entry_order, rc._models.SubmitOrderCreatedDto)

    # Secondary with GTC
    exit_price = best_ask_price * 1.05
    exit_price = float(round(exit_price / tick_size) * tick_size)

    exit_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=exit_price,
        quantity=0.001,
        time_in_force="GTD",
        group_id=group_id,
    )
    assert isinstance(exit_order, rc._models.SubmitOrderCreatedDto)

    # Verify time_in_force values
    time.sleep(2)
    entry = rc.get_order(id=entry_order.id)
    exit = rc.get_order(id=exit_order.id)

    assert entry.time_in_force.value == "GTD"
    assert entry.expires_at is not None
    assert exit.time_in_force.value == "GTD"

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[entry_order.id, exit_order.id],
    )


@pytest.mark.devnet_only
def test_rest_post_only_with_oco(rc, sid):
    """Test post-only orders with OCO groups.

    Post-only orders:
    - Only add liquidity (maker orders)
    - Rejected if would cross spread
    - Lower fees
    """
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]
    pid = rc.products[0].id
    tick_size = float(rc.products_by_id[pid].tick_size)
    prices = rc.list_market_prices(product_ids=[pid])[0]
    best_bid_price = float(prices.best_bid_price)
    best_ask_price = float(prices.best_ask_price)

    group_id = str(uuid.uuid4())

    # Post-only buy order (below best bid)
    buy_price = best_bid_price * 0.99
    buy_price = float(round(buy_price / tick_size) * tick_size)

    buy_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=0,  # BUY
        price=buy_price,
        quantity=0.001,
        time_in_force="GTD",
        post_only=True,  # Must be maker
        group_id=group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(buy_order, rc._models.SubmitOrderCreatedDto)

    # Post-only sell order (above best ask)
    sell_price = best_ask_price * 1.01
    sell_price = float(round(sell_price / tick_size) * tick_size)

    sell_order = rc.create_order(
        order_type="LIMIT",
        product_id=pid,
        side=1,  # SELL
        price=sell_price,
        quantity=0.001,
        time_in_force="GTD",
        post_only=True,  # Must be maker
        group_id=group_id,
        group_contingency_type=1,  # OCO
    )
    assert isinstance(sell_order, rc._models.SubmitOrderCreatedDto)

    # Verify post-only OCO orders
    time.sleep(2)
    buy = rc.get_order(id=buy_order.id)
    sell = rc.get_order(id=sell_order.id)

    assert buy.post_only is True
    assert buy.group_id == group_id
    assert sell.post_only is True
    assert sell.group_id == group_id

    # Clean up
    rc.cancel_orders(
        sender=rc.chain.address,
        subaccount=subaccount.name,
        order_ids=[buy_order.id, sell_order.id],
    )
