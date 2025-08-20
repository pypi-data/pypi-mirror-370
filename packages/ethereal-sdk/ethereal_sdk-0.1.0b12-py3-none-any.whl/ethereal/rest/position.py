from typing import List

from ethereal.constants import API_PREFIX
from ethereal.models.rest import (
    PositionDto,
    V1PositionGetParametersQuery,
    PageOfPositionDtos,
)


def list_positions(
    self,
    **kwargs,
) -> List[PositionDto]:
    """Lists positions for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        product_id (str, optional): UUID of the product to filter by. Optional.
        open (bool, optional): Filter for open positions. Optional.
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        order_by (str, optional): Field to order by, e.g., 'size', 'createdAt', or 'updatedAt'. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[PositionDto]: List of position information for the subaccount.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/position",
        request_model=V1PositionGetParametersQuery,
        response_model=PageOfPositionDtos,
        **kwargs,
    )
    data = [PositionDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def get_position(
    self,
    id: str,
    **kwargs,
) -> PositionDto:
    """Gets a specific position by ID.

    Args:
        id (str): UUID of the position. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        PositionDto: Position information for the specified ID.
    """
    endpoint = f"{API_PREFIX}/position/{id}"
    res = self.get(endpoint, **kwargs)
    return PositionDto(**res)
