from web3 import Web3


def test_provider(rc):
    rc.logger.info(f"Chain ID: {rc.chain.chain_id}")
    assert rc.provider is not None
    assert isinstance(rc.provider, Web3)


def test_block(rc):
    """Test block method."""
    block = rc.provider.eth.get_block("latest")
    assert block is not None
    assert block.get("number") is not None
    assert block.get("hash") is not None


def test_nonce(rc):
    """Test nonce method."""
    nonce = rc.chain.get_nonce(rc.chain.address)
    rc.logger.info(f"Nonce: {nonce}")
    assert nonce is not None


def test_gas(rc):
    """Test gas methods."""
    gas_price = rc.provider.eth.gas_price
    rc.logger.info(f"Gas Price: {gas_price}")
    assert gas_price is not None
    assert gas_price > 0

    max_priority_fee = rc.provider.eth.max_priority_fee
    rc.logger.info(f"Max Priority Fee: {max_priority_fee}")
    assert max_priority_fee is not None

    gas_limit = rc.provider.eth.estimate_gas(
        {"from": rc.chain.address, "to": rc.chain.address, "value": 1}
    )
    rc.logger.info(f"Gas Limit: {gas_limit}")
    assert gas_limit is not None
    assert gas_limit > 0


def test_eth_balance(rc):
    """Test eth balance method."""
    balance = rc.chain.get_balance(rc.chain.address)
    rc.logger.info(f"Balance: {balance}")
    assert balance is not None
    assert balance >= 0


def test_usde_balance(rc):
    """Test token balance method."""
    balance = rc.chain.get_token_balance(rc.chain.address, rc.chain.usde.address)
    rc.logger.info(f"Balance: {balance}")
    assert balance is not None
    assert balance >= 0


def test_deposit_usde(rc):
    """Test USDe deposit."""
    deposit_tx = rc.chain.deposit_usde(100)
    rc.logger.info(f"Deposit Tx: {deposit_tx}")

    assert deposit_tx is not None
    assert deposit_tx.get("data") is not None
    assert deposit_tx.get("value") == rc.chain.provider.to_wei(100, "ether")
    assert rc.provider.is_checksum_address(deposit_tx.get("from"))
    assert rc.provider.is_checksum_address(deposit_tx.get("to"))

    # estimate gas for the transaction
    gas_estimate = rc.provider.eth.estimate_gas(deposit_tx)
    assert gas_estimate is not None
    assert gas_estimate > 0

    # submit the transaction
    # tx_hash = rc.chain.submit_tx(deposit_tx)
    # rc.logger.info(f"Tx Hash: {tx_hash}")
