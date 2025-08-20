"""Test REST API calls for linking and revoking signers."""

import pytest
from uuid import UUID
from eth_account import Account
from ethereal.models.rest import (
    RevokeLinkedSignerDto,
    SignerDto,
    LinkSignerDto,
    LinkSignerDtoData,
)


@pytest.mark.skip(
    reason="Linked signers are rate limited, therefore running this test several times causes failure."
)
def test_link_and_revoke_signer(rc, sid, sname):
    """Test linking a random signer and revoking it."""
    # make a new account
    account = Account.create()

    link_signer_dto = rc.prepare_linked_signer(
        sender=rc.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # sign from the signer account
    link_signer_dto = rc.sign_linked_signer(
        link_signer_dto,
        private_key=rc.chain.private_key,
        signer_private_key=account.key,
    )

    # submit the link signer
    link_signer_result = rc.link_linked_signer(
        dto=link_signer_dto,
    )

    assert isinstance(link_signer_result, SignerDto)
    assert link_signer_result.signer == account.address

    # prepare the revoke linked signer
    revoke_dto = rc.prepare_revoke_linked_signer(
        sender=rc.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # sign the revoke linked signer
    revoke_dto = rc.sign_revoke_linked_signer(
        revoke_dto,
    )

    # submit the revoke linked signer
    revoke_linked_signer_result = rc.revoke_linked_signer(
        dto=revoke_dto,
    )

    assert isinstance(revoke_linked_signer_result, RevokeLinkedSignerDto)


def test_prepare_linked_signer(rc_ro, sid, sname):
    """Test preparing a linked signer without signing or submitting."""
    account = Account.create()

    link_signer_dto = rc_ro.prepare_linked_signer(
        sender=rc_ro.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # Verify the DTO was created correctly
    assert isinstance(link_signer_dto, LinkSignerDto)
    typed_data = LinkSignerDtoData.model_validate(
        link_signer_dto.data.model_dump(by_alias=True)
    )
    assert isinstance(typed_data, LinkSignerDtoData)
    assert link_signer_dto.signature == ""
    assert link_signer_dto.signer_signature == ""
    assert link_signer_dto.data.sender == rc_ro.chain.address
    assert link_signer_dto.data.signer == account.address
    assert link_signer_dto.data.subaccount_id == UUID(sid)


def test_prepare_and_sign_linked_signer_sender(rc, sid, sname):
    """Test preparing and signing a linked signer from the sender side without submitting."""
    account = Account.create()

    # Prepare the linked signer request
    link_signer_dto = rc.prepare_linked_signer(
        sender=rc.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # Sign from the sender account
    link_signer_dto = rc.sign_linked_signer(
        link_signer_dto,
        private_key=rc.chain.private_key,
    )
    # Verify it was signed correctly
    assert isinstance(link_signer_dto, LinkSignerDto)
    assert link_signer_dto.signature != ""
    assert link_signer_dto.signer_signature == ""


def test_prepare_and_sign_linked_signer_signer(rc_ro, sid, sname):
    """Test preparing and signing a linked signer from the signer side without submitting."""
    account = Account.create()

    # Prepare the linked signer request
    link_signer_dto = rc_ro.prepare_linked_signer(
        sender=rc_ro.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # Sign from the signer account
    link_signer_dto = rc_ro.sign_linked_signer(
        link_signer_dto,
        signer_private_key=account.key,
    )

    # Verify it was signed correctly
    assert isinstance(link_signer_dto, LinkSignerDto)
    assert link_signer_dto.signature == ""
    assert link_signer_dto.signer_signature != ""


def test_prepare_and_sign_linked_signer_both(rc, sid, sname):
    """Test preparing and signing a linked signer from both sender and signer without submitting."""
    account = Account.create()

    # Prepare the linked signer request
    link_signer_dto = rc.prepare_linked_signer(
        sender=rc.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # Sign with the sender's key
    link_signer_dto = rc.sign_linked_signer(
        link_signer_dto,
        private_key=rc.chain.private_key,
    )

    # Then sign with the signer's key
    link_signer_dto = rc.sign_linked_signer(
        link_signer_dto,
        signer_private_key=account.key,
    )

    # Verify both signatures are present
    assert isinstance(link_signer_dto, LinkSignerDto)
    assert link_signer_dto.signature != ""
    assert link_signer_dto.signer_signature != ""
    assert link_signer_dto.signature != link_signer_dto.signer_signature


def test_prepare_revoke_linked_signer(rc_ro, sid, sname):
    """Test preparing to revoke a linked signer without signing or submitting."""
    account = Account.create()

    revoke_dto = rc_ro.prepare_revoke_linked_signer(
        sender=rc_ro.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # Verify the DTO was created correctly
    assert isinstance(revoke_dto, RevokeLinkedSignerDto)
    assert revoke_dto.data.sender == rc_ro.chain.address
    assert revoke_dto.data.signer == account.address
    assert revoke_dto.data.subaccount_id == UUID(sid)
    assert revoke_dto.signature == ""


def test_prepare_and_sign_revoke_linked_signer(rc, sid, sname):
    """Test preparing and signing to revoke a linked signer without submitting."""
    account = Account.create()

    # Prepare the revocation request
    revoke_dto = rc.prepare_revoke_linked_signer(
        sender=rc.chain.address,
        signer=account.address,
        subaccount=sname,
        subaccount_id=sid,
    )

    # Sign the revocation
    revoke_dto = rc.sign_revoke_linked_signer(revoke_dto)

    # Verify it was signed correctly
    assert isinstance(revoke_dto, RevokeLinkedSignerDto)
    assert revoke_dto.signature != ""
