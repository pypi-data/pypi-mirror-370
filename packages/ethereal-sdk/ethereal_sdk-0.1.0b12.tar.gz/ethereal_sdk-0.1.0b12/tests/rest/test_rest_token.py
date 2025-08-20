"""Test REST API calls for token operations."""

import pytest
from ethereal.models.rest import WithdrawDto, InitiateWithdrawDto


def test_prepare_withdraw_token(rc_ro, sid):
    """Test preparing a token withdrawal without signing or submitting."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]

    if not rc_ro.list_tokens():
        pytest.skip("No tokens available for testing")

    token = rc_ro.list_tokens()[0]
    withdraw_params = {
        "subaccount": subaccount.name,
        "token": token.address,
        "amount": 100000,
        "account": rc_ro.chain.address,
    }

    withdraw_dto = rc_ro.prepare_withdraw_token(**withdraw_params)

    assert isinstance(withdraw_dto, InitiateWithdrawDto)
    assert withdraw_dto.data.token == token.address
    assert withdraw_dto.data.subaccount == subaccount.name
    assert withdraw_dto.data.amount == 100000
    assert withdraw_dto.data.account == rc_ro.chain.address
    assert withdraw_dto.signature == ""


def test_prepare_and_sign_withdraw_token(rc, sid):
    """Test preparing and signing a token withdrawal without submitting."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    if not rc.list_tokens():
        pytest.skip("No tokens available for testing")

    token = rc.list_tokens()[0]
    withdraw_params = {
        "subaccount": subaccount.name,
        "token": token.address,
        "amount": 100000,
        "account": rc.chain.address,
    }

    # Prepare the withdrawal
    withdraw_dto = rc.prepare_withdraw_token(**withdraw_params)

    # Sign the withdrawal
    signed_withdraw_dto = rc.sign_withdraw_token(withdraw_dto)

    # Verify it was signed correctly
    assert isinstance(signed_withdraw_dto, InitiateWithdrawDto)
    assert signed_withdraw_dto.signature != ""


def test_prepare_with_automatic_signing(rc, sid):
    """Test preparing a token withdrawal with automatic signing."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    token = rc.list_tokens()[0]
    withdraw_params = {
        "subaccount": subaccount.name,
        "token": token.address,
        "amount": 100000,
        "account": rc.chain.address,
        "include_signature": True,
    }

    # Prepare and sign the withdrawal in one step
    withdraw_dto = rc.prepare_withdraw_token(**withdraw_params)

    assert isinstance(withdraw_dto, InitiateWithdrawDto)
    assert withdraw_dto.signature != ""


def test_prepare_withdraw_token_with_custom_nonce(rc_ro, sid):
    """Test preparing a token withdrawal with a custom nonce."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]

    if not rc_ro.list_tokens():
        pytest.skip("No tokens available for testing")

    token = rc_ro.list_tokens()[0]
    custom_nonce = "123456789"

    withdraw_params = {
        "subaccount": subaccount.name,
        "token": token.address,
        "amount": 100000,
        "account": rc_ro.chain.address,
        "nonce": custom_nonce,
    }

    withdraw_dto = rc_ro.prepare_withdraw_token(**withdraw_params)

    assert isinstance(withdraw_dto, InitiateWithdrawDto)
    assert withdraw_dto.data.nonce == custom_nonce


def test_prepare_withdraw_token_with_custom_signed_at(rc_ro, sid):
    """Test preparing a token withdrawal with a custom signed_at timestamp."""
    subaccount = [s for s in rc_ro.subaccounts if s.id == sid][0]

    token = rc_ro.list_tokens()[0]
    custom_timestamp = 1620000000

    withdraw_params = {
        "subaccount": subaccount.name,
        "token": token.address,
        "amount": 100000,
        "account": rc_ro.chain.address,
        "signed_at": custom_timestamp,
    }

    withdraw_dto = rc_ro.prepare_withdraw_token(**withdraw_params)

    # Verify the DTO contains our custom timestamp
    assert isinstance(withdraw_dto, InitiateWithdrawDto)
    assert withdraw_dto.data.signed_at == custom_timestamp


@pytest.mark.skip(reason="This test actually submits a withdrawal request")
def test_prepare_sign_submit_withdraw_token(rc, sid):
    """Test preparing, signing, and submitting a token withdrawal."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    token = rc.list_tokens()[0]
    withdraw_params = {
        "subaccount": subaccount.name,
        "token": token.address,
        "amount": 100000,  # Small amount for testing
        "account": rc.chain.address,
    }

    # Prepare the withdrawal
    withdraw_dto = rc.prepare_withdraw_token(**withdraw_params)

    # Sign the withdrawal
    signed_withdraw_dto = rc.sign_withdraw_token(withdraw_dto)

    # Submit the withdrawal
    withdrawal_result = rc.withdraw_token(signed_withdraw_dto, token_id=token.id)

    # Verify the result
    assert isinstance(withdrawal_result, WithdrawDto)
    assert withdrawal_result.token == token.id
    assert withdrawal_result.subaccount_id == sid


@pytest.mark.skip(reason="This test actually submits a withdrawal request")
def test_prepare_sign_submit_withdraw_token_one_step(rc, sid):
    """Test preparing, signing, and submitting a token withdrawal in fewer steps."""
    subaccount = [s for s in rc.subaccounts if s.id == sid][0]

    token = rc.list_tokens()[0]
    withdraw_params = {
        "subaccount": subaccount.name,
        "token": token.address,
        "amount": 100000,
        "account": rc.chain.address,
        "include_signature": True,
    }

    # Prepare and sign the withdrawal in one step
    withdraw_dto = rc.prepare_withdraw_token(**withdraw_params)

    # Submit the withdrawal
    withdrawal_result = rc.withdraw_token(withdraw_dto, token_id=token.id)

    assert isinstance(withdrawal_result, WithdrawDto)
    assert withdrawal_result.token == token.id
    assert withdrawal_result.subaccount_id == sid
