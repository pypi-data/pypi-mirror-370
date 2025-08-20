import time
from decimal import Decimal
from typing import List, Optional

from ethereal.constants import API_PREFIX
from ethereal.models.rest import (
    TokenDto,
    WithdrawDto,
    TransferDto,
    InitiateWithdrawDto,
    InitiateWithdrawDtoData,
    V1TokenGetParametersQuery,
    V1TokenTransferGetParametersQuery,
    V1TokenWithdrawGetParametersQuery,
    PageOfTokensDtos,
    PageOfTransfersDtos,
    PageOfWithdrawDtos,
)
from ethereal.rest.util import generate_nonce


def list_tokens(
    self,
    **kwargs,
) -> List[TokenDto]:
    """Lists all tokens.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        deposit_enabled (bool, optional): Filter for deposit-enabled tokens. Optional.
        withdraw_enabled (bool, optional): Filter for withdraw-enabled tokens. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[TokenDto]: A list containing all token information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/token",
        request_model=V1TokenGetParametersQuery,
        response_model=PageOfTokensDtos,
        **kwargs,
    )
    data = [TokenDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def get_token(
    self,
    id: str,
    **kwargs,
) -> TokenDto:
    """Gets a specific token by ID.

    Args:
        id (str): The token identifier. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        TokenDto: The requested token information.
    """
    endpoint = f"{API_PREFIX}/token/{id}"
    res = self.get(endpoint, **kwargs)
    return TokenDto(**res)


def list_token_withdraws(
    self,
    **kwargs,
) -> List[WithdrawDto]:
    """Lists token withdrawals for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        active (bool, optional): Filter for active withdrawals. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[WithdrawDto]: A list of withdrawal information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/token/withdraw",
        request_model=V1TokenWithdrawGetParametersQuery,
        response_model=PageOfWithdrawDtos,
        **kwargs,
    )
    data = [WithdrawDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def list_token_transfers(
    self,
    **kwargs,
) -> List[TransferDto]:
    """Lists token transfers for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        statuses (List[str], optional): List of transfer statuses. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[TransferDto]: A list of transfer information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/token/transfer",
        request_model=V1TokenTransferGetParametersQuery,
        response_model=PageOfTransfersDtos,
        **kwargs,
    )
    data = [TransferDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def prepare_withdraw_token(
    self,
    subaccount: str,
    token: str,
    amount: int,
    account: str,
    include_signature: bool = False,
    **kwargs,
) -> InitiateWithdrawDto:
    """Prepares the data model and optionally the signature for a token withdrawal.

    Args:
        subaccount (str): Subaccount name as a bytes string
        token (str): Address of the token to withdraw
        amount (int): Amount to withdraw
        account (str): Address to withdraw to
        include_signature (bool, optional): Whether to include the signature. Defaults to False.

    Other Parameters:
        nonce (str, optional): Custom nonce for the withdraw. If not provided, one will be generated.
        signed_at (int, optional): Custom timestamp for the withdraw. If not provided, current time will be used.
        **kwargs: Additional parameters for the withdraw.

    Returns:
        InitiateWithdrawDto: DTO containing the data model and optionally the signature.

    Raises:
        ValueError: If include_signature is True and no chain client or private key is available.
    """
    nonce = kwargs.get("nonce") or generate_nonce()
    signed_at = kwargs.get("signed_at") or int(time.time())
    data = {
        "account": account,
        "subaccount": subaccount,
        "token": token,
        "amount": amount,
        "nonce": nonce,
        "signedAt": signed_at,
    }
    data_model = InitiateWithdrawDtoData.model_validate(data)
    dto = InitiateWithdrawDto.model_validate(
        {"data": data_model.model_dump(mode="json", by_alias=True), "signature": ""}
    )
    if include_signature:
        dto = self.sign_withdraw_token(dto)
    return dto


def sign_withdraw_token(
    self,
    withdraw_dto: InitiateWithdrawDto,
    private_key: Optional[str] = None,
) -> InitiateWithdrawDto:
    """Signs the token withdrawal data using the chain client.

    Args:
        withdraw_dto (InitiateWithdrawDto): Withdrawal data to sign.
        private_key (Optional[str], optional): Private key for signing. If None, uses the instance's private key.

    Returns:
        InitiateWithdrawDto: The signed withdrawal DTO with signature included.

    Raises:
        ValueError: If no chain client or private key is available.
    """
    if not hasattr(self, "chain") or not self.chain:
        raise ValueError("No chain client available for signing")
    if not private_key and not self.chain.private_key:
        raise ValueError("No private key available for signing")
    elif not private_key:
        private_key = self.chain.private_key

    # Prepare the message for signing
    message = withdraw_dto.data.model_dump(mode="json", by_alias=True)
    message["amount"] = int(Decimal(message["amount"]) * Decimal(1e9))
    message["signedAt"] = int(message["signedAt"])

    primary_type = "InitiateWithdraw"
    domain = self.rpc_config.domain.model_dump(mode="json", by_alias=True)
    types = self.chain.get_signature_types(self.rpc_config, primary_type)
    withdraw_dto.signature = self.chain.sign_message(
        private_key, domain, types, primary_type, message
    )
    return withdraw_dto


def withdraw_token(
    self,
    dto: InitiateWithdrawDto,
    token_id: str,
    **kwargs,
) -> WithdrawDto:
    """Submits a prepared and signed token withdrawal request.

    Args:
        dto (InitiateWithdrawDto): Prepared and signed withdrawal data.
        token_id (str): ID of the token to withdraw.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        WithdrawDto: Response containing the withdrawal information.
    """
    endpoint = f"{API_PREFIX}/token/{token_id}/withdraw"
    res = self.post(
        endpoint,
        data=dto.model_dump(mode="json", by_alias=True, exclude_none=True),
        **kwargs,
    )
    return WithdrawDto.model_validate(res)
