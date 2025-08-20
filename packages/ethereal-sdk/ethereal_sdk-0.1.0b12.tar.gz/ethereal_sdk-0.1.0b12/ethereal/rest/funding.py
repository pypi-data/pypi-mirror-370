from typing import List
from ethereal.constants import API_PREFIX
from ethereal.models.rest import (
    FundingDto,
    V1FundingGetParametersQuery,
    PageOfFundingDtos,
    V1FundingProjectedGetParametersQuery,
    ProjectedFundingDto,
)


def list_funding(self, **kwargs) -> List[FundingDto]:
    """Lists historical funding rates for a product over a specified time range.

    Args:
        product_id (str): Id representing the registered product. Required.
        range (str): The range of time of funding rates to retrieve. One of 'DAY', 'WEEK', or 'MONTH'. Required.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[FundingDto]: List of funding rate history objects for the product.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/funding",
        request_model=V1FundingGetParametersQuery,
        response_model=PageOfFundingDtos,
        **kwargs,
    )
    data = [FundingDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def get_projected_funding(self, **kwargs) -> ProjectedFundingDto:
    """Gets the projected funding rate for a product for the next hour.

    Args:
        product_id (str): Id representing the registered product. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        ProjectedFundingDto: Projected funding rate for the next hour for the product.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/funding/projected",
        request_model=V1FundingProjectedGetParametersQuery,
        response_model=ProjectedFundingDto,
        **kwargs,
    )
    return res
