# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .....types.v2 import Chain
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .stocks.stocks import (
    StocksResource,
    AsyncStocksResource,
    StocksResourceWithRawResponse,
    AsyncStocksResourceWithRawResponse,
    StocksResourceWithStreamingResponse,
    AsyncStocksResourceWithStreamingResponse,
)
from ....._base_client import make_request_options
from .....types.v2.chain import Chain
from .....types.v2.accounts import (
    OrderSide,
    OrderType,
    order_request_list_params,
    order_request_get_fee_quote_params,
    order_request_create_limit_buy_params,
    order_request_create_limit_sell_params,
    order_request_create_market_buy_params,
    order_request_create_market_sell_params,
)
from .....types.v2.accounts.order_side import OrderSide
from .....types.v2.accounts.order_type import OrderType
from .....types.v2.accounts.order_request import OrderRequest
from .....types.v2.accounts.order_request_list_response import OrderRequestListResponse
from .....types.v2.accounts.order_request_get_fee_quote_response import OrderRequestGetFeeQuoteResponse

__all__ = ["OrderRequestsResource", "AsyncOrderRequestsResource"]


class OrderRequestsResource(SyncAPIResource):
    @cached_property
    def stocks(self) -> StocksResource:
        return StocksResource(self._client)

    @cached_property
    def with_raw_response(self) -> OrderRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return OrderRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrderRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return OrderRequestsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        order_request_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Get a specific `OrderRequest` by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_request_id:
            raise ValueError(f"Expected a non-empty value for `order_request_id` but received {order_request_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/order_requests/{order_request_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    def list(
        self,
        account_id: str,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequestListResponse:
        """
        Lists `OrderRequests`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/order_requests",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    order_request_list_params.OrderRequestListParams,
                ),
            ),
            cast_to=OrderRequestListResponse,
        )

    def create_limit_buy(
        self,
        account_id: str,
        *,
        asset_quantity: float,
        limit_price: float,
        stock_id: str,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Create a managed `OrderRequest` to place a limit buy `Order`.

        Args:
          asset_quantity: Amount of dShare asset involved. Required for limit `Orders` and market sell
              `Orders`.

          limit_price: Price at which to execute the order. Must be a positive number with a precision
              of up to 2 decimal places.

          stock_id: ID of `Stock`.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/order_requests/limit_buy",
            body=maybe_transform(
                {
                    "asset_quantity": asset_quantity,
                    "limit_price": limit_price,
                    "stock_id": stock_id,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_limit_buy_params.OrderRequestCreateLimitBuyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    def create_limit_sell(
        self,
        account_id: str,
        *,
        asset_quantity: float,
        limit_price: float,
        stock_id: str,
        payment_token_address: str | NotGiven = NOT_GIVEN,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Create a managed `OrderRequest` to place a limit sell `Order`.

        Args:
          asset_quantity: Amount of dShare asset involved. Required for limit `Orders` and market sell
              `Orders`.

          limit_price: Price at which to execute the order. Must be a positive number with a precision
              of up to 2 decimal places.

          stock_id: ID of `Stock`.

          payment_token_address: Address of the payment token to be used for the sell order. If not provided, the
              default payment token (USD+) will be used. Should only be specified if
              `recipient_account_id` for a non-managed wallet account is also provided.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/order_requests/limit_sell",
            body=maybe_transform(
                {
                    "asset_quantity": asset_quantity,
                    "limit_price": limit_price,
                    "stock_id": stock_id,
                    "payment_token_address": payment_token_address,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_limit_sell_params.OrderRequestCreateLimitSellParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    def create_market_buy(
        self,
        account_id: str,
        *,
        payment_amount: float,
        stock_id: str,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """Create a managed `OrderRequest` to place a market buy `Order`.

        Fees for the
        `Order` are included in the transaction. Refer to our
        [Fee Quote API](https://docs.dinari.com/reference/createproxiedorderfeequote#/)
        for fee estimation.

        Args:
          payment_amount: Amount of currency (USD for US equities and ETFs) to pay for the order. Must be
              a positive number with a precision of up to 2 decimal places.

          stock_id: ID of `Stock`.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/order_requests/market_buy",
            body=maybe_transform(
                {
                    "payment_amount": payment_amount,
                    "stock_id": stock_id,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_market_buy_params.OrderRequestCreateMarketBuyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    def create_market_sell(
        self,
        account_id: str,
        *,
        asset_quantity: float,
        stock_id: str,
        payment_token_address: str | NotGiven = NOT_GIVEN,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Create a managed `OrderRequest` to place a market sell `Order`.

        Args:
          asset_quantity: Quantity of shares to trade. Must be a positive number with a precision of up to
              9 decimal places.

          stock_id: ID of `Stock`.

          payment_token_address: Address of the payment token to be used for the sell order. If not provided, the
              default payment token (USD+) will be used. Should only be specified if
              `recipient_account_id` for a non-managed wallet account is also provided.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/order_requests/market_sell",
            body=maybe_transform(
                {
                    "asset_quantity": asset_quantity,
                    "stock_id": stock_id,
                    "payment_token_address": payment_token_address,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_market_sell_params.OrderRequestCreateMarketSellParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    def get_fee_quote(
        self,
        account_id: str,
        *,
        order_side: OrderSide,
        order_type: OrderType,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        chain_id: Chain | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token_address: str | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequestGetFeeQuoteResponse:
        """Get fee quote data for an `Order Request`.

        This is provided primarily for
        informational purposes.

        Args:
          order_side: Indicates whether `Order Request` is a buy or sell.

          order_type: Type of `Order Request`.

          stock_id: The Stock ID associated with the Order Request

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Order Requests`.

          chain_id: CAIP-2 chain ID of the blockchain where the `Order Request` will be placed. If
              not provided, the default chain ID (eip155:42161) will be used.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Order Requests`.

          payment_token_address: Address of the payment token to be used for an order. If not provided, the
              default payment token (USD+) will be used.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Order Requests`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/order_requests/fee_quote",
            body=maybe_transform(
                {
                    "order_side": order_side,
                    "order_type": order_type,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "chain_id": chain_id,
                    "limit_price": limit_price,
                    "payment_token_address": payment_token_address,
                    "payment_token_quantity": payment_token_quantity,
                },
                order_request_get_fee_quote_params.OrderRequestGetFeeQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequestGetFeeQuoteResponse,
        )


class AsyncOrderRequestsResource(AsyncAPIResource):
    @cached_property
    def stocks(self) -> AsyncStocksResource:
        return AsyncStocksResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOrderRequestsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrderRequestsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrderRequestsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return AsyncOrderRequestsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        order_request_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Get a specific `OrderRequest` by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_request_id:
            raise ValueError(f"Expected a non-empty value for `order_request_id` but received {order_request_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/order_requests/{order_request_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    async def list(
        self,
        account_id: str,
        *,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequestListResponse:
        """
        Lists `OrderRequests`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/order_requests",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "page": page,
                        "page_size": page_size,
                    },
                    order_request_list_params.OrderRequestListParams,
                ),
            ),
            cast_to=OrderRequestListResponse,
        )

    async def create_limit_buy(
        self,
        account_id: str,
        *,
        asset_quantity: float,
        limit_price: float,
        stock_id: str,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Create a managed `OrderRequest` to place a limit buy `Order`.

        Args:
          asset_quantity: Amount of dShare asset involved. Required for limit `Orders` and market sell
              `Orders`.

          limit_price: Price at which to execute the order. Must be a positive number with a precision
              of up to 2 decimal places.

          stock_id: ID of `Stock`.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/order_requests/limit_buy",
            body=await async_maybe_transform(
                {
                    "asset_quantity": asset_quantity,
                    "limit_price": limit_price,
                    "stock_id": stock_id,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_limit_buy_params.OrderRequestCreateLimitBuyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    async def create_limit_sell(
        self,
        account_id: str,
        *,
        asset_quantity: float,
        limit_price: float,
        stock_id: str,
        payment_token_address: str | NotGiven = NOT_GIVEN,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Create a managed `OrderRequest` to place a limit sell `Order`.

        Args:
          asset_quantity: Amount of dShare asset involved. Required for limit `Orders` and market sell
              `Orders`.

          limit_price: Price at which to execute the order. Must be a positive number with a precision
              of up to 2 decimal places.

          stock_id: ID of `Stock`.

          payment_token_address: Address of the payment token to be used for the sell order. If not provided, the
              default payment token (USD+) will be used. Should only be specified if
              `recipient_account_id` for a non-managed wallet account is also provided.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/order_requests/limit_sell",
            body=await async_maybe_transform(
                {
                    "asset_quantity": asset_quantity,
                    "limit_price": limit_price,
                    "stock_id": stock_id,
                    "payment_token_address": payment_token_address,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_limit_sell_params.OrderRequestCreateLimitSellParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    async def create_market_buy(
        self,
        account_id: str,
        *,
        payment_amount: float,
        stock_id: str,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """Create a managed `OrderRequest` to place a market buy `Order`.

        Fees for the
        `Order` are included in the transaction. Refer to our
        [Fee Quote API](https://docs.dinari.com/reference/createproxiedorderfeequote#/)
        for fee estimation.

        Args:
          payment_amount: Amount of currency (USD for US equities and ETFs) to pay for the order. Must be
              a positive number with a precision of up to 2 decimal places.

          stock_id: ID of `Stock`.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/order_requests/market_buy",
            body=await async_maybe_transform(
                {
                    "payment_amount": payment_amount,
                    "stock_id": stock_id,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_market_buy_params.OrderRequestCreateMarketBuyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    async def create_market_sell(
        self,
        account_id: str,
        *,
        asset_quantity: float,
        stock_id: str,
        payment_token_address: str | NotGiven = NOT_GIVEN,
        recipient_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequest:
        """
        Create a managed `OrderRequest` to place a market sell `Order`.

        Args:
          asset_quantity: Quantity of shares to trade. Must be a positive number with a precision of up to
              9 decimal places.

          stock_id: ID of `Stock`.

          payment_token_address: Address of the payment token to be used for the sell order. If not provided, the
              default payment token (USD+) will be used. Should only be specified if
              `recipient_account_id` for a non-managed wallet account is also provided.

          recipient_account_id: ID of `Account` to receive the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/order_requests/market_sell",
            body=await async_maybe_transform(
                {
                    "asset_quantity": asset_quantity,
                    "stock_id": stock_id,
                    "payment_token_address": payment_token_address,
                    "recipient_account_id": recipient_account_id,
                },
                order_request_create_market_sell_params.OrderRequestCreateMarketSellParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequest,
        )

    async def get_fee_quote(
        self,
        account_id: str,
        *,
        order_side: OrderSide,
        order_type: OrderType,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        chain_id: Chain | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token_address: str | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRequestGetFeeQuoteResponse:
        """Get fee quote data for an `Order Request`.

        This is provided primarily for
        informational purposes.

        Args:
          order_side: Indicates whether `Order Request` is a buy or sell.

          order_type: Type of `Order Request`.

          stock_id: The Stock ID associated with the Order Request

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Order Requests`.

          chain_id: CAIP-2 chain ID of the blockchain where the `Order Request` will be placed. If
              not provided, the default chain ID (eip155:42161) will be used.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Order Requests`.

          payment_token_address: Address of the payment token to be used for an order. If not provided, the
              default payment token (USD+) will be used.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Order Requests`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/order_requests/fee_quote",
            body=await async_maybe_transform(
                {
                    "order_side": order_side,
                    "order_type": order_type,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "chain_id": chain_id,
                    "limit_price": limit_price,
                    "payment_token_address": payment_token_address,
                    "payment_token_quantity": payment_token_quantity,
                },
                order_request_get_fee_quote_params.OrderRequestGetFeeQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRequestGetFeeQuoteResponse,
        )


class OrderRequestsResourceWithRawResponse:
    def __init__(self, order_requests: OrderRequestsResource) -> None:
        self._order_requests = order_requests

        self.retrieve = to_raw_response_wrapper(
            order_requests.retrieve,
        )
        self.list = to_raw_response_wrapper(
            order_requests.list,
        )
        self.create_limit_buy = to_raw_response_wrapper(
            order_requests.create_limit_buy,
        )
        self.create_limit_sell = to_raw_response_wrapper(
            order_requests.create_limit_sell,
        )
        self.create_market_buy = to_raw_response_wrapper(
            order_requests.create_market_buy,
        )
        self.create_market_sell = to_raw_response_wrapper(
            order_requests.create_market_sell,
        )
        self.get_fee_quote = to_raw_response_wrapper(
            order_requests.get_fee_quote,
        )

    @cached_property
    def stocks(self) -> StocksResourceWithRawResponse:
        return StocksResourceWithRawResponse(self._order_requests.stocks)


class AsyncOrderRequestsResourceWithRawResponse:
    def __init__(self, order_requests: AsyncOrderRequestsResource) -> None:
        self._order_requests = order_requests

        self.retrieve = async_to_raw_response_wrapper(
            order_requests.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            order_requests.list,
        )
        self.create_limit_buy = async_to_raw_response_wrapper(
            order_requests.create_limit_buy,
        )
        self.create_limit_sell = async_to_raw_response_wrapper(
            order_requests.create_limit_sell,
        )
        self.create_market_buy = async_to_raw_response_wrapper(
            order_requests.create_market_buy,
        )
        self.create_market_sell = async_to_raw_response_wrapper(
            order_requests.create_market_sell,
        )
        self.get_fee_quote = async_to_raw_response_wrapper(
            order_requests.get_fee_quote,
        )

    @cached_property
    def stocks(self) -> AsyncStocksResourceWithRawResponse:
        return AsyncStocksResourceWithRawResponse(self._order_requests.stocks)


class OrderRequestsResourceWithStreamingResponse:
    def __init__(self, order_requests: OrderRequestsResource) -> None:
        self._order_requests = order_requests

        self.retrieve = to_streamed_response_wrapper(
            order_requests.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            order_requests.list,
        )
        self.create_limit_buy = to_streamed_response_wrapper(
            order_requests.create_limit_buy,
        )
        self.create_limit_sell = to_streamed_response_wrapper(
            order_requests.create_limit_sell,
        )
        self.create_market_buy = to_streamed_response_wrapper(
            order_requests.create_market_buy,
        )
        self.create_market_sell = to_streamed_response_wrapper(
            order_requests.create_market_sell,
        )
        self.get_fee_quote = to_streamed_response_wrapper(
            order_requests.get_fee_quote,
        )

    @cached_property
    def stocks(self) -> StocksResourceWithStreamingResponse:
        return StocksResourceWithStreamingResponse(self._order_requests.stocks)


class AsyncOrderRequestsResourceWithStreamingResponse:
    def __init__(self, order_requests: AsyncOrderRequestsResource) -> None:
        self._order_requests = order_requests

        self.retrieve = async_to_streamed_response_wrapper(
            order_requests.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            order_requests.list,
        )
        self.create_limit_buy = async_to_streamed_response_wrapper(
            order_requests.create_limit_buy,
        )
        self.create_limit_sell = async_to_streamed_response_wrapper(
            order_requests.create_limit_sell,
        )
        self.create_market_buy = async_to_streamed_response_wrapper(
            order_requests.create_market_buy,
        )
        self.create_market_sell = async_to_streamed_response_wrapper(
            order_requests.create_market_sell,
        )
        self.get_fee_quote = async_to_streamed_response_wrapper(
            order_requests.get_fee_quote,
        )

    @cached_property
    def stocks(self) -> AsyncStocksResourceWithStreamingResponse:
        return AsyncStocksResourceWithStreamingResponse(self._order_requests.stocks)
