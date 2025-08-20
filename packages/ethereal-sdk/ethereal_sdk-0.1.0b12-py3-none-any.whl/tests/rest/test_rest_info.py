"""Test simple REST API informational calls that do not require existing accounts"""

import pytest
from typing import List
import uuid
from ethereal.models.rest import (
    RpcConfigDto,
    SubaccountDto,
    FundingDto,
    ProjectedFundingDto,
    ProductDto,
    MarketLiquidityDto,
    MarketPriceDto,
    TokenDto,
)
from ethereal.rest.http_client import ValidationException


def test_rest_subaccounts(rc):
    """Test retrieving subaccounts for a given address."""
    subaccounts = rc.list_subaccounts(sender=rc.chain.address)
    assert isinstance(subaccounts, List)
    assert all(isinstance(sa, SubaccountDto) for sa in subaccounts)


def test_rest_subaccount(rc):
    """Test retrieving a single subaccount for a given address."""
    subaccounts = rc.list_subaccounts(sender=rc.chain.address)
    subaccount = rc.get_subaccount(subaccounts[0].id)
    assert isinstance(subaccount, SubaccountDto)


def test_rest_rpc_config(rc):
    """Test retrieving RPC configuration."""
    rpc_config = rc.get_rpc_config()
    assert isinstance(rpc_config, RpcConfigDto)


def test_rest_funding_rates(rc):
    """Test retrieving funding rates for a specific product over a month period."""
    pid = rc.products[0].id
    funding_rates = rc.list_funding(product_id=pid, range="MONTH")
    assert isinstance(funding_rates, List)
    assert all(isinstance(sa, FundingDto) for sa in funding_rates)


def test_rest_projected_funding(rc):
    """Test retrieving projected funding rates for a specific product."""
    pid = rc.products[0].id
    projected_funding = rc.get_projected_funding(product_id=pid)
    assert isinstance(projected_funding, ProjectedFundingDto)


def test_rest_products(rc):
    """Test retrieving list of available products."""
    products = rc.list_products()
    assert isinstance(products, List)
    assert all(isinstance(p, ProductDto) for p in products)


def test_rest_market_liquidity(rc):
    """Test retrieving market liquidity for a specific product."""
    pid = rc.products[0].id
    market_liquidity = rc.get_market_liquidity(product_id=pid)
    assert isinstance(market_liquidity, MarketLiquidityDto)


def test_rest_market_liquidity_with_bad_inputs(rc):
    """Test calling market liquidity function with bad inputs."""
    invalid_pid = uuid.uuid4()  # a random UUID

    # no inputs
    with pytest.raises(ValidationException):
        rc.get_market_liquidity()

    with pytest.raises(Exception):
        rc.get_market_liquidity(product_id=invalid_pid)


def test_rest_market_prices(rc):
    """Test retrieving market prices for multiple products."""
    pids = [p.id for p in rc.products[:20]]
    market_prices = rc.list_market_prices(product_ids=pids)
    assert isinstance(market_prices, List)
    assert all(isinstance(mp, MarketPriceDto) for mp in market_prices)


def test_rest_token_property(rc):
    """Test retrieving list of available tokens from the token property."""
    tokens = rc.tokens
    assert isinstance(tokens, List)
    assert all(isinstance(t, TokenDto) for t in tokens)


def test_rest_list_tokens(rc):
    """Test retrieving list of available tokens."""
    tokens = rc.list_tokens()
    assert isinstance(tokens, List)
    assert all(isinstance(t, TokenDto) for t in tokens)


def test_rest_get_token(rc):
    """Test retrieving a specific token by ID."""
    tokens = rc.list_tokens()
    token = rc.get_token(tokens[0].id)
    assert isinstance(token, TokenDto)
    assert token.id == tokens[0].id
