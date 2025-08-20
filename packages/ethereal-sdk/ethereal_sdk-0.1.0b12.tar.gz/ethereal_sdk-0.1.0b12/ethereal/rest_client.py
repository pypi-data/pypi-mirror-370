from __future__ import annotations
import importlib
from pydantic import BaseModel, ValidationError, AnyHttpUrl
from typing import TYPE_CHECKING, Union, Dict, Any, Optional, Type, List, Tuple
from functools import cached_property
from ethereal.constants import API_PREFIX, NETWORK_URLS
from ethereal.rest.http_client import HTTPClient
from ethereal.chain_client import ChainClient
from ethereal.models.config import RESTConfig, ChainConfig

from ethereal.rest.funding import list_funding, get_projected_funding
from ethereal.rest.order import (
    get_order,
    list_fills,
    list_orders,
    list_trades,
    prepare_order,
    sign_order,
    submit_order,
    dry_run_order,
    prepare_cancel_order,
    sign_cancel_order,
    cancel_order,
)
from ethereal.rest.linked_signer import (
    get_signer,
    get_signer_quota,
    list_signers,
    prepare_linked_signer,
    sign_linked_signer,
    link_linked_signer,
    prepare_revoke_linked_signer,
    sign_revoke_linked_signer,
    revoke_linked_signer,
)
from ethereal.rest.position import list_positions, get_position
from ethereal.rest.product import (
    get_market_liquidity,
    list_market_prices,
    list_products,
)
from ethereal.rest.rpc import get_rpc_config
from ethereal.rest.subaccount import (
    list_subaccounts,
    get_subaccount,
    get_subaccount_balances,
)
from ethereal.rest.token import (
    get_token,
    list_token_withdraws,
    list_tokens,
    list_token_transfers,
    prepare_withdraw_token,
    sign_withdraw_token,
    withdraw_token,
)

_MODEL_PATHS = {
    "default": "ethereal.models.rest",
    "testnet": "ethereal.models.testnet.rest",
    "devnet": "ethereal.models.devnet.rest",
}

if TYPE_CHECKING:
    from ethereal.models.rest import *  # noqa: F403


def _override_models(network: str = "default") -> None:
    """Populate this module's globals with models for a network.

    This allows other helpers that import model names from this module
    (e.g., via from ethereal.rest_client import SomeDto) to resolve
    to network-specific types.
    """
    pkg = importlib.import_module(_MODEL_PATHS.get(network, _MODEL_PATHS["default"]))
    # if the module defines __all__, use that; else grab all UPPER‑case names
    public = getattr(pkg, "__all__", [n for n in dir(pkg) if n[0].isupper()])
    for name in public:
        globals()[name] = getattr(pkg, name)


# Default to base models at import time; instance will override per network
_override_models()


class PaginatedResponse(BaseModel):
    data: Any
    has_next: bool
    next_cursor: Optional[str]


class RESTClient(HTTPClient):
    """
    REST client for interacting with the Ethereal API.

    Args:
        config (Union[Dict[str, Any], RESTConfig], optional): Configuration dictionary or RESTConfig object. Optional fields include:
            private_key (str, optional): The private key.
            base_url (str, optional): Base URL for REST requests. Defaults to "https://api.etherealtest.net".
            timeout (int, optional): Timeout in seconds for REST requests.
            verbose (bool, optional): Enables debug logging. Defaults to False.
            rate_limit_headers (bool, optional): Enables rate limit headers. Defaults to False.
    """

    list_funding = list_funding
    get_projected_funding = get_projected_funding
    get_order = get_order
    list_fills = list_fills
    list_orders = list_orders
    list_trades = list_trades
    prepare_order = prepare_order
    sign_order = sign_order
    submit_order = submit_order
    dry_run_order = dry_run_order
    prepare_cancel_order = prepare_cancel_order
    sign_cancel_order = sign_cancel_order
    cancel_order = cancel_order
    get_signer = get_signer
    get_signer_quota = get_signer_quota
    list_signers = list_signers
    prepare_linked_signer = prepare_linked_signer
    sign_linked_signer = sign_linked_signer
    link_linked_signer = link_linked_signer
    prepare_revoke_linked_signer = prepare_revoke_linked_signer
    sign_revoke_linked_signer = sign_revoke_linked_signer
    revoke_linked_signer = revoke_linked_signer
    list_positions = list_positions
    get_position = get_position
    get_market_liquidity = get_market_liquidity
    list_market_prices = list_market_prices
    list_products = list_products
    get_rpc_config = get_rpc_config
    list_subaccounts = list_subaccounts
    get_subaccount = get_subaccount
    get_subaccount_balances = get_subaccount_balances
    get_token = get_token
    list_token_withdraws = list_token_withdraws
    list_tokens = list_tokens
    list_token_transfers = list_token_transfers
    prepare_withdraw_token = prepare_withdraw_token
    sign_withdraw_token = sign_withdraw_token
    withdraw_token = withdraw_token

    def __init__(self, config: Union[Dict[str, Any], RESTConfig] = {}):
        self.config = RESTConfig.model_validate(config)

        # Set base_url from network if not provided
        network = self.config.network or "testnet"
        # Bind network-specific models on the instance and update module globals
        self._models = importlib.import_module(
            _MODEL_PATHS.get(network, _MODEL_PATHS["default"])  # type: ignore
        )
        _override_models(network)
        if not self.config.base_url:
            self.config.base_url = AnyHttpUrl(
                NETWORK_URLS.get(network, NETWORK_URLS["testnet"])
            )

        super().__init__(self.config)

        # fetch RPC configuration
        self.chain: Optional[ChainClient] = None
        self.rpc_config = self.get_rpc_config()
        if self.config.chain_config:
            self._init_chain_client(
                self.config.chain_config, self.rpc_config, self.tokens
            )
        self.private_key = self.chain.private_key if self.chain else None
        self.provider = self.chain.provider if self.chain else None

        self.default_time_in_force = self.config.default_time_in_force
        self.default_post_only = self.config.default_post_only

    def _init_chain_client(
        self,
        config: Union[Dict[str, Any], ChainConfig],
        rpc_config: Optional[RpcConfigDto] = None,
        tokens: Optional[List[TokenDto]] = None,
    ):
        """Initialize the ChainClient.

        Args:
            config (Union[Dict[str, Any], ChainConfig]): The chain configuration.
            rpc_config (RpcConfigDto, optional): RPC configuration. Defaults to None.
        """
        config = ChainConfig.model_validate(config)
        try:
            self.chain = ChainClient(config, rpc_config, tokens)
            self.logger.info("Chain client initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize chain client: {e}")

    def _get_pages(
        self,
        endpoint: str,
        request_model: Type[BaseModel],
        response_model: Type[BaseModel],
        paginate: bool = False,
        **kwargs,
    ) -> Any:
        """Make a GET request with validated parameters and response and handling for pagination.

        Args:
            endpoint (str): API endpoint path (e.g. "order" will be appended to the base URL and prefix to form "/v1/order")
            request_model (BaseModel): Pydantic model for request validation
            response_model (BaseModel): Pydantic model for response validation
            paginate (bool): Whether to fetch additional pages of data
            **kwargs: Parameters to validate and include in the request

        Returns:
            response (BaseModel): Validated response object

        Example:
            orders = client.validated_get(
                endpoint="order",
                request_model=V1OrderGetParametersQuery,
                response_model=PageOfOrderDtos,
                subaccount_id="abc123",
                limit=50
            )
        """
        result = self.get_validated(
            url_path=f"{API_PREFIX}/{endpoint}",
            request_model=request_model,
            response_model=response_model,
            **kwargs,
        )

        # If pagination is requested, fetch additional pages
        try:
            page_response = response_model.model_validate(result)
        except ValidationError as e:
            raise e
        if paginate:
            all_data = list(page_response.data)  # type: ignore

            # Continue fetching while there are more pages
            current_result = page_response
            while current_result.has_next and current_result.next_cursor:  # type: ignore
                new_result = self.get_validated(
                    url_path=f"{API_PREFIX}/{endpoint}",
                    request_model=request_model,
                    response_model=response_model,
                    cursor=current_result.next_cursor,  # type: ignore
                    **kwargs,
                )
                # Add data from this page
                current_result = response_model.model_validate(new_result)
                all_data.extend(current_result.data)  # type: ignore

            # Update the result with the combined data
            page_response.data = all_data  # type: ignore
            page_response.has_next = False  # type: ignore
            page_response.next_cursor = None  # type: ignore
        return page_response.data  # type: ignore

    @cached_property
    def subaccounts(self):
        """Get the list of subaccounts in the order they were created.

        Returns:
            subaccounts (List): List of subaccount objects.
        """
        return self.list_subaccounts(
            sender=self.chain.address, order_by="createdAt", order="asc"
        )

    @cached_property
    def products(self):
        """Get the list of products.

        Returns:
            products (List): List of product objects.
        """
        return self.list_products()

    @cached_property
    def tokens(self):
        """Get the list of tokens.

        Returns:
            tokens (List): List of token objects.
        """
        return self.list_tokens()

    @cached_property
    def products_by_ticker(self):
        """Get the products indexed by ticker.

        Returns:
            products_by_ticker (Dict[str, ProductDto]): Dictionary of products keyed by ticker.
        """
        return {p.ticker: p for p in self.products}

    @cached_property
    def products_by_id(self):
        """Get the products indexed by ID.

        Returns:
            products_by_id (Dict[str, ProductDto]): Dictionary of products keyed by ID.
        """
        return {p.id: p for p in self.products}

    def create_order(
        self,
        order_type: str,
        quantity: float,
        side: int,
        price: Optional[float] = None,
        ticker: Optional[str] = None,
        product_id: Optional[str] = None,
        sender: Optional[str] = None,
        subaccount: Optional[str] = None,
        time_in_force: Optional[str] = None,
        post_only: Optional[bool] = None,
        reduce_only: Optional[bool] = False,
        close: Optional[bool] = None,
        stop_price: Optional[float] = None,
        stop_type: Optional[int] = None,
        expires_at: Optional[int] = None,
        otoco_trigger: Optional[bool] = None,
        otoco_group_id: Optional[str] = None,
        group_id: Optional[str] = None,
        group_contingency_type: Optional[int] = None,
        sign: bool = True,
        dry_run: bool = False,
        submit: bool = True,
    ):
        """Create and submit an order.

        Args:
            order_type (str): The type of order (market or limit)
            quantity (float): The quantity of the order
            side (int): The side of the order (0 = BUY, 1 = SELL)
            price (float, optional): The price of the order (for limit orders)
            ticker (str, optional): The ticker of the product
            product_id (str, optional): The ID of the product
            sender (str, optional): The sender address
            subaccount (str, optional): The subaccount name
            time_in_force (str, optional): The time in force for limit orders
            post_only (bool, optional): Whether the order is post-only (for limit orders)
            reduce_only (bool, optional): Whether the order is reduce only
            close (bool, optional): Whether the order is a close order
            stop_price (float, optional): The stop price for stop orders
            stop_type (int, optional): The stop type (0 = STOP, 1 = STOP_LIMIT)
            expires_at (int, optional): The expiration timestamp for the order
            otoco_trigger (bool, optional): [LEGACY] Creates a new OTO group with this order as trigger
            otoco_group_id (str, optional): [LEGACY] Joins an existing OTO/OCO group
            group_id (str, optional): Group ID for OTO/OCO relationships (preferred over legacy params)
            group_contingency_type (int, optional): Contingency type - 0=OTO (One-Triggers-Other), 1=OCO (One-Cancels-Other)
            dry_run (bool, optional): Whether to perform a dry run (no actual order submission)

        Returns:
            Union[SubmitOrderCreatedDto, DryRunOrderCreatedDto, SubmitOrderDto]: The created order object, dry run result, or result from order submission.

        Raises:
            ValueError: If neither product_id nor ticker is provided or if order type is invalid
        """
        # get the sender and account info
        if sender is None and self.chain:
            sender = self.chain.address
        if subaccount is None:
            subaccount = self.subaccounts[0].name

        # get the product info
        if product_id is not None:
            onchain_id = self.products_by_id[product_id].onchain_id
        elif ticker is not None:
            onchain_id = self.products_by_ticker[ticker].onchain_id
        else:
            raise ValueError("Either product_id or ticker must be provided")

        # prepare the order params
        if order_type == "MARKET":
            order_params = {
                "sender": sender,
                "subaccount": subaccount,
                "side": side,
                "price": "0",
                "quantity": quantity,
                "onchain_id": onchain_id,
                "order_type": order_type,
                "reduce_only": reduce_only,
                "dryrun": dry_run,
                "close": close,
                "stop_price": stop_price,
                "stop_type": stop_type,
                # Include all OTO/OCO params, prepare_order will handle network-specific mapping
                "otoco_trigger": otoco_trigger,
                "otoco_group_id": otoco_group_id,
                "group_id": group_id,
                "group_contingency_type": group_contingency_type,
            }
        elif order_type == "LIMIT":
            order_params = {
                "sender": sender,
                "subaccount": subaccount,
                "side": side,
                "price": price,
                "quantity": quantity,
                "onchain_id": onchain_id,
                "order_type": order_type,
                "time_in_force": time_in_force or self.default_time_in_force,
                "post_only": post_only or self.default_post_only,
                "reduce_only": reduce_only,
                "close": close,
                "stop_price": stop_price,
                "stop_type": stop_type,
                # Include all OTO/OCO params, prepare_order will handle network-specific mapping
                "otoco_trigger": otoco_trigger,
                "otoco_group_id": otoco_group_id,
                "group_id": group_id,
                "group_contingency_type": group_contingency_type,
                "expires_at": expires_at,
                "dryrun": dry_run,
            }
        else:
            raise ValueError("Invalid order type")

        order = self.prepare_order(**order_params, include_signature=sign)
        if dry_run:
            return self.dry_run_order(order)
        elif submit:
            return self.submit_order(order)
        else:
            return order

    def cancel_orders(
        self,
        order_ids: List[str],
        sender: str,
        subaccount: str,
        sign: bool = True,
        submit: bool = True,
        **kwargs,
    ) -> Union[List[CancelOrderResultDto], CancelOrderDto]:
        """Prepares and optionally submits a request to cancel multiple orders.

        Args:
            order_ids (List[str]): List of order UUIDs to cancel
            sender (str): Address of the sender
            subaccount (str): Subaccount address
            sign (bool, optional): Whether to sign the request. Defaults to True.
            submit (bool, optional): Whether to submit the request to the API. Defaults to True.

        Returns:
            Union[List[CancelOrderResultDto], CancelOrderDto]: List of cancellation results or the prepared cancel order data.
        """
        if len(order_ids) == 0:
            raise ValueError("No order IDs provided for cancellation")
        try:
            prepared_cancel = self.prepare_cancel_order(
                order_ids=order_ids,
                sender=sender,
                subaccount=subaccount,
                include_signature=sign,
                **kwargs,
            )
        except ValueError as e:
            self.logger.warning(f"Could not prepare/sign order cancellation: {e}")
            raise

        if not submit:
            return prepared_cancel

        # Submit the cancellation request
        result = self.cancel_order(
            prepared_cancel,
            **kwargs,
        )
        return result

    def cancel_all_orders(
        self,
        subaccount_id: str,
        product_ids: Optional[List[str]] = None,
        **kwargs,
    ) -> List[CancelOrderResultDto]:
        """
        Cancel all orders for a given subaccount.

        Args:
            subaccount_id (str): The ID of the subaccount.
            product_ids (List[str], optional): The IDs of the products to filter orders. If not provided, all orders will be canceled.
            **kwargs: Additional parameters for the request.

        Returns:
            List[CancelOrderResultDto]: The results of the cancel operations.
        """
        subaccount = self.get_subaccount(id=subaccount_id)
        query_params = {
            "subaccount_id": subaccount_id,
            "statuses": ["FILLED_PARTIAL", "NEW", "PENDING"],
            **kwargs,
        }
        if product_ids:
            query_params["product_ids"] = product_ids

        orders = self._get_pages(
            endpoint="order",
            request_model=self._models.V1OrderGetParametersQuery,
            response_model=self._models.PageOfOrderDtos,
            paginate=True,
            **query_params,
        )
        order_ids = [order.id for order in orders]

        # cancel all orders
        if len(order_ids) == 0:
            raise ValueError("No order IDs provided for cancellation")
        cancel_results = self.cancel_orders(
            order_ids=order_ids,
            sender=subaccount.account,
            subaccount=subaccount.name,
            sign=True,
            submit=True,
        )
        if not isinstance(cancel_results, list):
            raise ValueError("Failed to cancel orders")
        return cancel_results

    def replace_order(
        self,
        order: Optional[OrderDto] = None,
        order_id: Optional[str] = None,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        time_in_force: Optional[str] = None,
        post_only: Optional[bool] = None,
        reduce_only: Optional[bool] = False,
    ) -> Tuple[SubmitOrderCreatedDto, bool]:
        """
        Replace an existing order.

        Args:
            order (OrderDto, optional): The order to replace.
            order_id (str, optional): The ID of the order to replace.
            quantity (float, optional): The new quantity of the order.
            price (float, optional): The new price of the order (for limit orders).
            time_in_force (str, optional): The time in force for limit orders.
            post_only (bool, optional): Whether the order is post-only (for limit orders).
            reduce_only (bool, optional): Whether the order is reduce only.

        Returns:
            Tuple[SubmitOrderCreatedDto, bool]: The response data from the API and a success flag for the cancel operation.

        Raises:
            ValueError: If neither order nor order_id is provided, or if both are provided.
        """
        # get the order info
        if order is None and order_id is None:
            raise ValueError("Either order or order_id must be provided")
        elif order is not None and order_id is not None:
            raise ValueError("Only one of order or order_id must be provided")
        elif order is not None:
            old_order = order
        elif order_id is not None:
            old_order = self.get_order(id=order_id)
        subaccount = self.get_subaccount(id=old_order.subaccount_id)

        # set default values
        if quantity is None:
            quantity = float(old_order.quantity)
        if price is None:
            price = float(old_order.price)
        if time_in_force is None:
            time_in_force = (
                old_order.time_in_force.value if old_order.time_in_force else None
            )
        if post_only is None:
            post_only = old_order.post_only
        if reduce_only is None:
            reduce_only = old_order.reduce_only

        # cancel the old order
        cancel_result = self.cancel_orders(
            order_ids=[old_order.id],
            sender=old_order.sender,
            subaccount=subaccount.name,
            sign=True,
            submit=True,
        )
        if not isinstance(cancel_result, list) or len(cancel_result) != 1:
            raise ValueError("Failed to cancel order")
        canceled_order = cancel_result[0]

        if not canceled_order.result.value == "Ok":
            raise ValueError(
                f"Failed to cancel order {order_id}: {canceled_order.result.value}"
            )

        # create the new order params
        new_order = self.create_order(
            order_type=old_order.type.value,
            quantity=quantity,
            side=old_order.side.value,
            price=price,
            product_id=old_order.product_id,
            sender=old_order.sender,
            subaccount=subaccount.name,
            time_in_force=time_in_force or self.default_time_in_force,
            post_only=post_only or self.default_post_only,
            reduce_only=reduce_only,
            dry_run=False,
        )
        return self._models.SubmitOrderCreatedDto.model_validate(
            new_order
        ), canceled_order.result.value == "Ok"
