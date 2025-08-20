from typing import List
from ethereal.constants import API_PREFIX
from ethereal.models.rest import (
    SubaccountDto,
    SubaccountBalanceDto,
    V1SubaccountGetParametersQuery,
    PageOfSubaccountDtos,
    V1SubaccountBalanceGetParametersQuery,
    PageOfSubaccountBalanceDtos,
)


def list_subaccounts(self, **kwargs) -> List[SubaccountDto]:
    """Lists subaccounts for a sender.

    Args:
        sender (str): Address of the account which registered the subaccount. Required.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        name (str, optional): Filter by subaccount name. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[SubaccountDto]: List of subaccount information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/subaccount/",
        request_model=V1SubaccountGetParametersQuery,
        response_model=PageOfSubaccountDtos,
        **kwargs,
    )
    data = [SubaccountDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def get_subaccount(self, id: str, **kwargs) -> SubaccountDto:
    """Gets a specific subaccount by ID.

    Args:
        id (str): UUID of the subaccount. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        SubaccountDto: Subaccount information.
    """
    endpoint = f"{API_PREFIX}/subaccount/{id}"
    res = self.get(endpoint, **kwargs)
    return SubaccountDto(**res)


def get_subaccount_balances(self, **kwargs) -> List[SubaccountBalanceDto]:
    """Gets balances for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[SubaccountBalanceDto]: List of balance information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/subaccount/balance",
        request_model=V1SubaccountBalanceGetParametersQuery,
        response_model=PageOfSubaccountBalanceDtos,
        **kwargs,
    )
    data = [
        SubaccountBalanceDto(**model.model_dump(by_alias=True)) for model in res.data
    ]
    return data
