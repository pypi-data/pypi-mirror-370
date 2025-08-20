from web3 import Web3
from ethereal.models.config import (
    BaseConfig,
    HTTPConfig,
    WSConfig,
    ChainConfig,
    RESTConfig,
)
from ethereal.base_client import BaseClient
from ethereal.rest.http_client import HTTPClient
from ethereal.ws.ws_base import WSBase
from ethereal.chain_client import ChainClient
from ethereal.rest_client import RESTClient

BASE_URL = "https://api.etherealtest.net"
RPC_URL = "https://rpc.etherealtest.net"
WS_URL = "wss://ws.etherealtest.net"


def test_base_client_with_dict():
    bc = BaseClient({"verbose": True})
    assert bc is not None


def test_base_client_with_class():
    config = BaseConfig(verbose=True)
    bc = BaseClient(config)
    assert bc is not None


def test_http_client_with_dict():
    hc = HTTPClient({"base_url": BASE_URL, "verbose": True})
    assert hc is not None


def test_ws_client_with_class():
    config = WSConfig(base_url=WS_URL, verbose=True)
    hc = WSBase(config)
    assert hc is not None


def test_ws_client_with_dict():
    wsc = WSBase({"base_url": WS_URL, "verbose": True})
    assert wsc is not None


def test_http_client_with_class():
    config = HTTPConfig(base_url=BASE_URL, timeout=60, verbose=True)
    wsc = HTTPClient(config)
    assert wsc is not None


def test_chain_client_with_dict():
    test_account = Web3().eth.account.create()
    private_key = test_account.key.hex()

    cc = ChainClient(
        {
            "rpc_url": RPC_URL,
            "private_key": private_key,
        }
    )
    assert cc is not None
    assert cc.chain_id == 657468


def test_chain_client_with_class():
    test_account = Web3().eth.account.create()
    private_key = test_account.key.hex()

    config = ChainConfig(
        rpc_url=RPC_URL,
        private_key=private_key,
    )
    cc = ChainClient(config)
    assert cc is not None
    assert cc.chain_id == 657468


def test_rest_chain_client_with_dict():
    test_account = Web3().eth.account.create()
    private_key = test_account.key.hex()

    rc = RESTClient(
        {
            "base_url": BASE_URL,
            "chain_config": {
                "private_key": private_key,
                "rpc_url": RPC_URL,
            },
        }
    )
    assert rc is not None
    assert rc.chain.chain_id == 657468


def test_rest_chain_client_with_class():
    test_account = Web3().eth.account.create()
    private_key = test_account.key.hex()

    chain_config = ChainConfig(
        rpc_url=RPC_URL,
        private_key=private_key,
    )

    config = RESTConfig(
        base_url=BASE_URL,
        chain_config=chain_config,
    )
    rc = RESTClient(config)
    assert rc is not None
    assert rc.chain.chain_id == 657468


def test_rest_client_with_dict():
    rc = RESTClient()
    assert rc is not None
    assert rc.chain is None


def test_rest_client_with_class():
    config = RESTConfig()
    rc = RESTClient(config)
    assert rc is not None
    assert rc.chain is None
