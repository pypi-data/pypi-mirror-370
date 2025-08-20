from typing import List, Optional
from ethereal.constants import API_PREFIX
from ethereal.models.rest import (
    LinkSignerDto,
    LinkSignerDtoData,
    RevokeLinkedSignerDto,
    RevokeLinkedSignerDtoData,
    SignerDto,
    AccountSignerQuotaDto,
    V1LinkedSignerGetParametersQuery,
    PageOfSignersDto,
    V1LinkedSignerQuotaGetParametersQuery,
)
from ethereal.rest.util import generate_nonce
import time


def list_signers(
    self,
    **kwargs,
) -> List[SignerDto]:
    """Lists all linked signers for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        active (bool, optional): Filter for active signers. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[SignerDto]: List of linked signers for the subaccount.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/linked-signer",
        request_model=V1LinkedSignerGetParametersQuery,
        response_model=PageOfSignersDto,
        **kwargs,
    )
    data = [SignerDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def get_signer(
    self,
    id: str,
    **kwargs,
) -> SignerDto:
    """Gets a specific linked signer by ID.

    Args:
        id (str): UUID of the signer. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        SignerDto: Linked signer information.
    """
    endpoint = f"{API_PREFIX}/linked-signer/{id}"
    res = self.get(endpoint, **kwargs)
    return SignerDto.model_validate(res)


def get_signer_quota(
    self,
    **kwargs,
) -> AccountSignerQuotaDto:
    """Gets the signer quota for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        AccountSignerQuotaDto: Account signer quota information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/linked-signer/quota",
        request_model=V1LinkedSignerQuotaGetParametersQuery,
        response_model=AccountSignerQuotaDto,
        **kwargs,
    )
    return res


def prepare_linked_signer(
    self,
    sender: str,
    signer: str,
    subaccount: str,
    subaccount_id: str,
    signer_signature: str = "",
    include_signature: bool = False,
    **kwargs,
) -> LinkSignerDto:
    """Prepares the data for linking a signer without signing or submitting.

    Args:
        sender (str): Address of the sender. Required.
        signer (str): Address of the signer to be linked. Required.
        subaccount (str): Address of the subaccount. Required.
        subaccount_id (str): UUID of the subaccount. Required.

    Returns:
        LinkSignerDto: DTO containing the data model and signatures.
    """
    nonce = kwargs.get("nonce") or generate_nonce()
    signed_at = kwargs.get("signed_at") or int(time.time())
    data = {
        "sender": sender,
        "signer": signer,
        "subaccount": subaccount,
        "subaccountId": subaccount_id,
        "nonce": nonce,
        "signedAt": signed_at,
    }
    data_model = LinkSignerDtoData.model_validate(data)

    # Prepare dto
    dto_data = {
        "data": data_model.model_dump(mode="json", by_alias=True),
        "signature": "",
        "signerSignature": signer_signature,
    }
    dto = LinkSignerDto.model_validate(dto_data, by_alias=True)
    if include_signature:
        dto = self.sign_linked_signer(dto, private_key=self.chain.private_key)
    return dto


def sign_linked_signer(
    self,
    link_to_sign: LinkSignerDto,
    signer_private_key: Optional[str] = None,
    private_key: Optional[str] = None,
) -> LinkSignerDto:
    """Signs the data for linking a signer without submitting.

    This function signs the prepared data for linking a signer. The message is prepared
    and signed with the private keys provided. If no private key is provided for either
    the signer or the sender, the signature will remain empty. If both private keys are
    provided, or the sender's private key is available in the chain client, the message will be
    signed and the signature will be included in the returned DTO.

    Args:
        link_to_sign: The prepared LinkSignerDto from prepare_link_signer
        signer_private_key: The private key of the signer being linked. Optional.
        private_key: The private key of the sender. Optional.

    Returns:
        LinkSignerDto: DTO containing the data model and signature

    Raises:
        ValueError: If the chain client or private key is not available
    """
    if not hasattr(self, "chain") or not self.chain:
        raise ValueError("No chain client available for signing")
    if not private_key and not self.chain.private_key and not signer_private_key:
        raise ValueError("No private key available for signing")
    elif not private_key:
        private_key = self.chain.private_key

    # Prepare message for signing
    message = link_to_sign.data.model_dump(mode="json", by_alias=True)
    message["signedAt"] = int(message["signedAt"])

    primary_type = "LinkSigner"
    domain = self.rpc_config.domain.model_dump(mode="json", by_alias=True)
    types = self.chain.get_signature_types(self.rpc_config, primary_type)

    if signer_private_key:
        signer_signature = self.chain.sign_message(
            signer_private_key, domain, types, primary_type, message
        )
        link_to_sign.signer_signature = signer_signature
    if self.chain.private_key:
        signature = self.chain.sign_message(
            private_key, domain, types, primary_type, message
        )
        link_to_sign.signature = signature
    return link_to_sign


def link_linked_signer(
    self,
    dto: LinkSignerDto,
    **kwargs,
) -> SignerDto:
    """Submits a prepared and signed LinkSignerDto to link a signer."""
    endpoint = f"{API_PREFIX}/linked-signer/link"
    res = self.post(
        endpoint,
        data=dto.model_dump(mode="json", by_alias=True, exclude_none=True),
        **kwargs,
    )
    return SignerDto.model_validate(res)


def prepare_revoke_linked_signer(
    self,
    sender: str,
    signer: str,
    subaccount: str,
    subaccount_id: str,
    include_signature: bool = False,
    **kwargs,
) -> RevokeLinkedSignerDto:
    """Prepares the data for revoking a linked signer without signing or submitting.

    Args:
        sender (str): Address of the sender. Required.
        signer (str): Address of the signer to be revoked. Required.
        subaccount (str): Address of the subaccount. Required.
        subaccount_id (str): UUID of the subaccount. Required.

    Returns:
        RevokeLinkedSignerDto: DTO containing the data model and signatures.
    """
    nonce = kwargs.get("nonce") or generate_nonce()
    signed_at = kwargs.get("signed_at") or int(time.time())
    data = {
        "sender": sender,
        "signer": signer,
        "subaccount": subaccount,
        "subaccountId": subaccount_id,
        "nonce": nonce,
        "signedAt": signed_at,
    }
    data_model = RevokeLinkedSignerDtoData.model_validate(data)
    dto = RevokeLinkedSignerDto.model_validate(
        {"data": data_model.model_dump(mode="json", by_alias=True), "signature": ""}
    )
    if include_signature:
        dto = self.sign_revoke_linked_signer(dto)
    return dto


def sign_revoke_linked_signer(
    self,
    revoke_to_sign: RevokeLinkedSignerDto,
) -> RevokeLinkedSignerDto:
    """Signs the data for revoking a linked signer without submitting.

    Args:
        revoke_to_sign: The prepared RevokeLinkedSignerDto from prepare_revoke_linked_signer

    Returns:
        RevokeLinkedSignerDto: DTO containing the data model and signature

    Raises:
        ValueError: If the chain client or private key is not available
    """
    if not hasattr(self, "chain") or not self.chain:
        raise ValueError("No chain client available for signing")
    if not self.chain.private_key:
        raise ValueError("No private key available for signing")

    # Prepare message for signing
    message = revoke_to_sign.data.model_dump(mode="json", by_alias=True)
    message["signedAt"] = int(message["signedAt"])

    primary_type = "RevokeLinkedSigner"
    domain = self.rpc_config.domain.model_dump(mode="json", by_alias=True)
    types = self.chain.get_signature_types(self.rpc_config, primary_type)
    revoke_to_sign.signature = self.chain.sign_message(
        self.chain.private_key, domain, types, primary_type, message
    )
    return revoke_to_sign


def revoke_linked_signer(
    self,
    dto: RevokeLinkedSignerDto,
    **kwargs,
) -> SignerDto:
    """Submits a prepared and signed RevokeLinkedSignerDto to revoke a linked signer."""
    endpoint = f"{API_PREFIX}/linked-signer/revoke"
    res = self.post(
        endpoint,
        data=dto.model_dump(mode="json", by_alias=True, exclude_none=True),
        **kwargs,
    )
    return SignerDto.model_validate(res)
