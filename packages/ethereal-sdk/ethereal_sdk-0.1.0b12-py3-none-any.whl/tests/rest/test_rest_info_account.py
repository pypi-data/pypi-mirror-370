"""Test simple REST API informational calls that require an account"""

from typing import List
from ethereal.models.rest import (
    PositionDto,
    TransferDto,
    WithdrawDto,
    SubaccountBalanceDto,
    SignerDto,
    PageOfOrderFillDtos,
    V1OrderFillGetParametersQuery,
)


def test_rest_info_subaccount_balances(rc, sid):
    """Test retrieving balances for a specific subaccount."""
    subaccount_balances = rc.get_subaccount_balances(subaccount_id=sid)
    assert isinstance(subaccount_balances, List)
    assert all(isinstance(sb, SubaccountBalanceDto) for sb in subaccount_balances)


def test_rest_info_orders(rc, sid):
    """Test retrieving list of orders for a specific subaccount."""
    orders = rc.list_orders(subaccount_id=sid)
    assert isinstance(orders, List)
    assert all(isinstance(o, rc._models.OrderDto) for o in orders)


def test_rest_info_fills(rc, sid):
    """Test retrieving list of fills for a specific subaccount."""
    fills = rc.list_fills(subaccount_id=sid)
    assert isinstance(fills, List)
    assert all(isinstance(f, rc._models.OrderFillDto) for f in fills)


def test_rest_info_fills_paginated(rc, sid):
    """Test retrieving list of fills for a specific subaccount by pages."""
    fills = rc._get_pages(
        endpoint="order/fill",
        request_model=rc._models.V1OrderFillGetParametersQuery,
        response_model=rc._models.PageOfOrderFillDtos,
        subaccount_id=sid,
        limit=500,
        paginate=True,
    )
    assert isinstance(fills, List)
    assert all(isinstance(f, rc._models.OrderFillDto) for f in fills)


def test_rest_info_trades(rc, sid):
    """Test retrieving list of trades."""
    params = {
        "product_id": rc.products[0].id,
        "order": "desc",
        "limit": 100,
    }
    trades = rc.list_trades(**params)
    assert isinstance(trades, List)
    assert all(isinstance(t, rc._models.TradeDto) for t in trades)


def test_rest_info_positions(rc, sid):
    """Test retrieving list of positions for a specific subaccount."""
    positions = rc.list_positions(subaccount_id=sid)
    assert isinstance(positions, List)
    assert all(isinstance(f, PositionDto) for f in positions)


def test_rest_info_trades_read_only(rc_ro, sid):
    """Test retrieving list of trades from a read-only client."""
    params = {
        "product_id": rc_ro.products[0].id,
        "order": "desc",
        "limit": 100,
    }
    trades = rc_ro.list_trades(**params)
    assert isinstance(trades, List)
    assert all(isinstance(t, rc_ro._models.TradeDto) for t in trades)


def test_rest_info_transfers(rc, sid):
    """Test retrieving list of transfers for a specific subaccount."""
    transfers = rc.list_token_transfers(subaccount_id=sid)
    assert isinstance(transfers, List)
    assert all(isinstance(t, TransferDto) for t in transfers)


def test_rest_info_withdraws(rc, sid):
    """Test retrieving list of withdraws for a specific subaccount."""
    withdraws = rc.list_token_withdraws(subaccount_id=sid)
    assert isinstance(withdraws, List)
    assert all(isinstance(w, WithdrawDto) for w in withdraws)


def test_rest_info_linked_signers(rc, sid):
    """Test retrieving list of linked signers for a specific subaccount."""
    linked_signers = rc.list_signers(subaccount_id=sid)
    assert isinstance(linked_signers, List)
    assert all(isinstance(ls, SignerDto) for ls in linked_signers)
