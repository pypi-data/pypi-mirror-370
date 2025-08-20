import time
from typing import List, Optional, Union
from decimal import Decimal
from uuid import UUID
from ethereal.constants import API_PREFIX
from ethereal.rest.util import generate_nonce, uuid_to_bytes32
from ethereal.models.rest import (
    OrderDto,
    OrderFillDto,
    TradeDto,
    SubmitOrderDto,
    SubmitOrderLimitDtoData,
    SubmitOrderMarketDtoData,
    CancelOrderDto,
    CancelOrderResultDto,
    DryRunOrderCreatedDto,
    SubmitOrderCreatedDto,
)


def list_orders(self, **kwargs) -> List[OrderDto]:
    """Lists orders for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        product_ids (List[str], optional): List of product UUIDs to filter. Optional.
        created_after (float, optional): Filter for orders created after this timestamp. Optional.
        created_before (float, optional): Filter for orders created before this timestamp. Optional.
        side (int, optional): Order side (BUY = 0, SELL = 1). Optional.
        close (bool, optional): Filter for close orders. Optional.
        stop_types (List[int], optional): List of stop types. Optional.
        statuses (List[str], optional): List of order statuses. Optional.
        order_by (str, optional): Field to order by, e.g., 'type'. Optional.
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        PageOfOrderDtos: List of order information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/order",
        request_model=self._models.V1OrderGetParametersQuery,
        response_model=self._models.PageOfOrderDtos,
        **kwargs,
    )
    data = [
        self._models.OrderDto(**model.model_dump(by_alias=True)) for model in res.data
    ]
    return data


def list_fills(
    self,
    **kwargs,
) -> List[OrderFillDto]:
    """Lists order fills for a subaccount.

    Args:
        subaccount_id (str): UUID of the subaccount. Required.

    Other Parameters:
        product_ids (List[str], optional): List of product UUIDs to filter. Optional.
        created_after (float, optional): Filter for fills created after this timestamp. Optional.
        created_before (float, optional): Filter for fills created before this timestamp. Optional.
        side (int, optional): Fill side (BUY = 0, SELL = 1). Optional.
        statuses (List[str], optional): List of fill statuses. Optional.
        order_by (str, optional): Field to order by, e.g., 'productId'. Optional.
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        include_self_trades (bool, optional): Whether to include self trades. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        PageOfOrderFillDtos: List of order fill information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/order/fill",
        request_model=self._models.V1OrderFillGetParametersQuery,
        response_model=self._models.PageOfOrderFillDtos,
        **kwargs,
    )
    data = [
        self._models.OrderFillDto(**model.model_dump(by_alias=True))
        for model in res.data
    ]
    return data


def list_trades(
    self,
    **kwargs,
) -> List[TradeDto]:
    """Lists trades for a product if specified, otherwise lists trades for all products.

    Other Parameters:
        product_id (str, optional): UUID of the product. Optional.
        order_by (str, optional): Field to order by, e.g., 'createdAt'. Optional.
        order (str, optional): Sort order, 'asc' or 'desc'. Optional.
        limit (float, optional): Maximum number of results to return. Optional.
        cursor (str, optional): Pagination cursor for fetching the next page. Optional.
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        PageOfTradeDtos: List of trade information.
    """
    res = self.get_validated(
        url_path=f"{API_PREFIX}/order/trade",
        request_model=self._models.V1OrderTradeGetParametersQuery,
        response_model=self._models.PageOfTradeDtos,
        **kwargs,
    )
    data = [
        self._models.TradeDto(**model.model_dump(by_alias=True)) for model in res.data
    ]
    return data


def get_order(self, id: str, **kwargs) -> OrderDto:
    """Gets a specific order by ID.

    Args:
        id (str): UUID of the order. Required.

    Other Parameters:
        **kwargs: Additional request parameters accepted by the API. Optional.

    Returns:
        OrderDto: Order information.
    """
    endpoint = f"{API_PREFIX}/order/{id}"
    response = self.get(endpoint, **kwargs)
    return self._models.OrderDto(**response)


def prepare_order(
    self,
    sender: str,
    price: Union[str, float, Decimal],
    quantity: Union[str, float, Decimal],
    side: int,
    subaccount: str,
    onchain_id: float,
    order_type: str,
    time_in_force: Optional[str] = None,
    post_only: Optional[bool] = False,
    reduce_only: Optional[bool] = False,
    close: Optional[bool] = None,
    stop_price: Optional[Union[str, float, Decimal]] = None,
    stop_type: Optional[int] = None,
    otoco_trigger: Optional[bool] = None,
    otoco_group_id: Optional[str] = None,
    group_id: Optional[str] = None,
    group_contingency_type: Optional[int] = None,
    expires_at: Optional[int] = None,
    include_signature: bool = False,
    **kwargs,
) -> SubmitOrderDto:
    """Prepares the data model and optionally the signature for an order submission.

    Args:
        sender (str): Address of the sender
        price (str): Order price
        quantity (str): Order quantity
        side (int): Order side (BUY = 0, SELL = 1)
        subaccount (str): Subaccount address
        onchain_id (float): On-chain ID of the product
        order_type (str): Order type (LIMIT or MARKET)
        time_in_force (str, optional): Time in force for limit orders. Defaults to None.
        post_only (bool, optional): Whether the order is post-only. Defaults to False.
        reduce_only (bool, optional): Whether the order is reduce-only. Defaults to False.
        close (bool, optional): Whether the order closes a position. Defaults to None.
        stop_price (float, optional): Stop price for stop orders. Defaults to None.
        stop_type (int, optional): Stop type for stop orders. Defaults to None.
        otoco_trigger (bool, optional): [LEGACY] Creates a new OTO group with this order as trigger. Defaults to None.
        otoco_group_id (str, optional): [LEGACY] Joins an existing OTO/OCO group. Defaults to None.
        group_id (str, optional): Group ID for OTO/OCO relationships (preferred over legacy params). Defaults to None.
        group_contingency_type (int, optional): Contingency type - 0=OTO (One-Triggers-Other), 1=OCO (One-Cancels-Other). Defaults to None.
        expires_at (int, optional): Expiration timestamp for the order. Defaults to None.
        include_signature (bool, optional): Whether to include the signature. Defaults to False.

    Returns:
        Dict[str, Any]: Dictionary containing the data model and optionally the signature.

    Raises:
        ValueError: If include_signature is True and no chain client or private key is available.
    """
    # Generate nonce and signed_at timestamp
    nonce = kwargs.get("nonce", None) or generate_nonce()
    signed_at = kwargs.get("signed_at", None) or int(time.time())

    # Prepare order data with common fields
    order_data = {
        "sender": sender,
        "subaccount": subaccount,
        "quantity": quantity,
        "price": price,
        "side": side,
        "engineType": 0,
        "onchainId": onchain_id,
        "nonce": nonce,
        "type": order_type,
        "reduceOnly": reduce_only,
        "signedAt": signed_at,
        "close": close,
        "stopPrice": stop_price,
        "stopType": stop_type,
        "otocoTrigger": otoco_trigger,
        "otocoGroupId": otoco_group_id,
        "groupId": group_id,
        "groupContingencyType": group_contingency_type,
        "expiresAt": expires_at,
    }

    # Declare data_model type
    data_model: Union[SubmitOrderLimitDtoData, SubmitOrderMarketDtoData]

    # Create specific order data based on type
    if order_type == "LIMIT":
        order_data.update(
            {
                "timeInForce": time_in_force,
                "postOnly": post_only,
            }
        )
        data_model = self._models.SubmitOrderLimitDtoData.model_validate(order_data)
    elif order_type == "MARKET":
        data_model = self._models.SubmitOrderMarketDtoData.model_validate(order_data)
    else:
        raise ValueError(f"Invalid order type: {order_type}")

    result = self._models.SubmitOrderDto.model_validate(
        {
            "data": data_model.model_dump(
                mode="json", by_alias=True, exclude_unset=True, exclude_none=True
            ),
            "signature": "",
        }
    )

    if include_signature:
        result = self.sign_order(result)

    return result


def sign_order(
    self, order: SubmitOrderDto, private_key: Optional[str] = None
) -> SubmitOrderDto:
    """Signs the order data using the chain client.

    Args:
        order (SubmitOrderDto): Order data to sign.
        private_key (Optional[str]): Private key for signing. If None, uses the instance's private key.

    Returns:
        str: Signature of the order data.

    Raises:
        ValueError: If no chain client or private key is available.
    """
    if not hasattr(self, "chain") or not self.chain:
        raise ValueError("No chain client available for signing")
    if not private_key and not self.chain.private_key:
        raise ValueError("No private key available for signing")
    elif not private_key:
        private_key = self.chain.private_key

    # Update message signedAt
    order.data.signed_at = int(time.time())

    # Prepare message for signing
    message = order.data.model_dump(mode="json", by_alias=True)

    # Make some adjustments to the message
    message["quantity"] = int(Decimal(message["quantity"]) * Decimal("1e9"))
    message["price"] = int(Decimal(message.get("price", 0)) * Decimal("1e9"))
    message["productId"] = int(message["onchainId"])
    message["signedAt"] = int(message["signedAt"])

    # Get domain and types for signing
    primary_type = "TradeOrder"
    domain = self.rpc_config.domain.model_dump(mode="json", by_alias=True)
    types = self.chain.get_signature_types(self.rpc_config, primary_type)

    # Sign the message
    order.signature = self.chain.sign_message(
        self.chain.private_key, domain, types, primary_type, message
    )
    return order


def submit_order(
    self,
    order: SubmitOrderDto,
    **kwargs,
) -> SubmitOrderCreatedDto:
    """Submits a prepared and signed order.

    Args:
        order (SubmitOrderDto): Prepared and signed order data.

    Returns:
        SubmitOrderCreatedDto: Response containing the order information.
    """
    endpoint = f"{API_PREFIX}/order"
    res = self.post(
        endpoint,
        data=order.model_dump(
            mode="json", by_alias=True, exclude_unset=True, exclude_none=True
        ),
        **kwargs,
    )
    return self._models.SubmitOrderCreatedDto.model_validate(res)


def dry_run_order(
    self,
    order: SubmitOrderDto,
    **kwargs,
) -> DryRunOrderCreatedDto:
    """Submits a prepared order for a dry run.

    Args:
        order (SubmitOrderDto): Prepared and signed order data.

    Returns:
        OrderDryRunDto: Response containing the dry run order information.
    """
    submit_payload = self._models.SubmitDryOrderDto.model_validate(
        {"data": order.data.model_dump(mode="json", by_alias=True, exclude_unset=True)}
    )
    endpoint = f"{API_PREFIX}/order/dry-run"
    res = self.post(
        endpoint,
        data=submit_payload.model_dump(
            mode="json", by_alias=True, exclude_unset=True, exclude_none=True
        ),
        **kwargs,
    )
    return self._models.DryRunOrderCreatedDto.model_validate(res)


def prepare_cancel_order(
    self,
    order_ids: List[str],
    sender: str,
    subaccount: str,
    include_signature: bool = False,
    **kwargs,
) -> CancelOrderDto:
    """Prepares the data model and optionally the signature for cancelling orders.

    Args:
        order_ids (List[str]): List of order UUIDs to cancel
        sender (str): Address of the sender
        subaccount (str): Subaccount address
        include_signature (bool, optional): Whether to include the signature. Defaults to False.

    Returns:
        Dict[str, Any]: Dictionary containing the data model and optionally the signature.

    Raises:
        ValueError: If include_signature is True and no chain client or private key is available.
    """
    nonce = kwargs.get("nonce", None) or generate_nonce()
    uuid_order_ids = [
        UUID(order_id) if isinstance(order_id, str) else order_id
        for order_id in order_ids
    ]
    data_model = self._models.CancelOrderDtoData(
        sender=sender,
        subaccount=subaccount,
        nonce=nonce,
        orderIds=uuid_order_ids,
    )
    result = self._models.CancelOrderDto.model_validate(
        {"data": data_model.model_dump(mode="json", by_alias=True), "signature": ""}
    )
    if include_signature:
        return self.sign_cancel_order(result)
    return result


def sign_cancel_order(
    self,
    order_to_cancel: CancelOrderDto,
    private_key: Optional[str] = None,
) -> CancelOrderDto:
    """Signs the cancel order data model.

    Args:
        order_to_cancel (CancelOrderDto): The order data model to sign.
        private_key (Optional[str]): Private key for signing. If None, uses the instance's private key.

    Returns:
        CancelOrderDto: The signed order data model.
    """
    if not hasattr(self, "chain") or not self.chain:
        raise ValueError("No chain client available for signing")
    if not private_key and not self.chain.private_key:
        raise ValueError("No private key available for signing")
    elif not private_key:
        private_key = self.chain.private_key

    # Prepare message for signing
    message = order_to_cancel.data.model_dump(mode="json", by_alias=True)

    # For cancel orders, orderIds need to be converted to bytes32 format
    order_ids = [
        uuid_to_bytes32(str(order_id)) for order_id in order_to_cancel.data.order_ids
    ]
    message["orderIds"] = order_ids

    # Get domain and types for signing
    primary_type = "CancelOrder"
    domain = self.rpc_config.domain.model_dump(mode="json", by_alias=True)
    types = self.chain.get_signature_types(self.rpc_config, primary_type)

    # Sign the message
    order_to_cancel.signature = self.chain.sign_message(
        self.chain.private_key, domain, types, primary_type, message
    )
    return order_to_cancel


def cancel_order(
    self,
    order_to_cancel: CancelOrderDto,
    **kwargs,
) -> List[CancelOrderResultDto]:
    """Submits a prepared and signed cancel order.

    Args:
        order_to_cancel (CancelOrderDto): Prepared and signed cancel order data.

    Returns:
        List[CancelOrderResultDto]: List of responses containing the cancellation results.
    """
    endpoint = f"{API_PREFIX}/order/cancel"
    res = self.post(
        endpoint,
        data=order_to_cancel.model_dump(mode="json", by_alias=True, exclude_none=True),
        **kwargs,
    )
    return [
        self._models.CancelOrderResultDto.model_validate(item)
        for item in res.get("data", [])
    ]
