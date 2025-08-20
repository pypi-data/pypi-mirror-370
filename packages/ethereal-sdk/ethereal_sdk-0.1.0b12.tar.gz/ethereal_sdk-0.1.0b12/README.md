# Ethereal Python SDK

A Python library for interacting with the Ethereal trading platform. This SDK provides tools for trading, managing positions, and accessing market data.

## SDK Documentation

For full documentation, visit the [documentation site](https://meridianxyz.github.io/ethereal-py-sdk/).

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the SDK
uv add ethereal-sdk
```

### Using pip

```bash
pip install ethereal-sdk
```

## Quick Start

```python
from ethereal import RESTClient

# Create a client
config = {
    "base_url": "https://api.etherealtest.net",
    "chain_config": {
        "rpc_url": "https://rpc.etherealtest.net"
        "private_key": "your_private_key",  # optional
    }
}
client = RESTClient()

# Get market data
products = client.list_products()
prices = client.list_market_prices()

# Place an order (NOTE: Private key and account are required)
client.create_order(
    order_type="limit",
    quantity=1.0,
    side=0,  # 0 for buy, 1 for sell
    price=100.0,
    ticker="BTCUSD"
)
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone git@github.com:meridianxyz/ethereal-py-sdk.git
cd ethereal-py-sdk

# Install dependencies with uv
uv sync

# Run tests
uv run pytest

# Run the linter
uv run ruff check --fix

# Run the example CLI
uv run python -i examples/cli.py
```

## Main Features

### Market Data

- List available trading products
- Get current market prices
- View market order book
- Track funding rates

### Trading

- Place market and limit orders
- Cancel orders
- View order history
- Track trades and fills

### Account Management

- Manage subaccounts
- View positions
- Track token balances
- Handle deposits and withdrawals

### Websocket Support

- Real-time market data
- Live order book updates

## Configuration

The SDK can be configured with these options:

- `private_key`: Your private key for authentication
- `base_url`: API endpoint (default: "https://api.etherealtest.net")
- `timeout`: Request timeout in seconds
- `verbose`: Enable debug logging
- `rate_limit_headers`: Enable rate limit headers

## Examples

### Get Market Data

```python
# List all available products
products = client.list_products()

# Get current prices
all_product_ids = [product.id for product in products]
prices = client.list_market_prices(productIds=all_product_ids)

# View market liquidity
btc_product_id = client.products_by_ticker['BTCUSD'].id
liquidity = client.get_market_liquidity(productId=btc_product_id)
```

### Manage Orders

```python
# Place a limit order
order = client.create_order(
    order_type="limit",
    quantity=1.0,
    side=0,
    price=100.0,
    ticker="BTCUSD"
)

# Cancel an order
client.cancel_order(orderId="<uuid of order>")

# View order history
subaccount_id = client.subaccounts[0].id
orders = client.list_orders(subaccountId=subaccount_id)
```

### Account Operations

```python
# List subaccounts
subaccounts = client.subaccounts

# View positions
positions = client.list_positions(subaccountId=subaccounts[0].id)

# Get token balances
balances = client.get_subaccount_balances(subaccountId=subaccounts[0].id)
```

## Error Handling

The SDK includes built-in error handling for:

- Invalid requests
- Authentication errors
- Rate limiting
- Network issues

## Ethereal Documentation

For full documentation, visit our [documentation site](https://docs.ethereal.trade).

## Support

For issues and questions, please refer to the project's issue tracker or documentation.
