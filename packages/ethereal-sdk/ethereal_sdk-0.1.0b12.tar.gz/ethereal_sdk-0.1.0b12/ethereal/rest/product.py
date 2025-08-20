from typing import List

from ethereal.constants import API_PREFIX
from ethereal.models.rest import (
    ProductDto,
    MarketLiquidityDto,
    MarketPriceDto,
    V1ProductGetParametersQuery,
    PageOfProductDtos,
    V1ProductMarketLiquidityGetParametersQuery,
    V1ProductMarketPriceGetParametersQuery,
    ListOfMarketPriceDtos,
)


def list_products(self, **kwargs) -> List[ProductDto]:
    """Lists all products and their configurations.

    Other Parameters:
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        ticker (str, optional): Product ticker to filter by. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[ProductDto]: List of product configurations.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/product",
        request_model=V1ProductGetParametersQuery,
        response_model=PageOfProductDtos,
        **kwargs,
    )
    data = [ProductDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data


def get_market_liquidity(self, **kwargs) -> MarketLiquidityDto:
    """Gets market liquidity for a product.

    Args:
        product_id (str): UUID of the product. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        MarketLiquidityDto: Market liquidity information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/product/market-liquidity",
        request_model=V1ProductMarketLiquidityGetParametersQuery,
        response_model=MarketLiquidityDto,
        **kwargs,
    )
    return res


def list_market_prices(self, **kwargs) -> List[MarketPriceDto]:
    """Gets market prices for multiple products.

    Args:
        product_ids (List[str]): List of product UUIDs. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        List[MarketPriceDto]: List of market prices.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/product/market-price",
        request_model=V1ProductMarketPriceGetParametersQuery,
        response_model=ListOfMarketPriceDtos,
        **kwargs,
    )
    data = [MarketPriceDto(**model.model_dump(by_alias=True)) for model in res.data]
    return data
