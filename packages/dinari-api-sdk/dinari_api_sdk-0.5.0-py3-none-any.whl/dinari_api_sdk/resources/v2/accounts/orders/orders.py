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
from .....types.v2.accounts import order_list_params, order_get_fulfillments_params
from .....types.v2.accounts.order import Order
from .....types.v2.accounts.order_list_response import OrderListResponse
from .....types.v2.accounts.order_get_fulfillments_response import OrderGetFulfillmentsResponse

__all__ = ["OrdersResource", "AsyncOrdersResource"]


class OrdersResource(SyncAPIResource):
    @cached_property
    def stocks(self) -> StocksResource:
        return StocksResource(self._client)

    @cached_property
    def with_raw_response(self) -> OrdersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return OrdersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrdersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return OrdersResourceWithStreamingResponse(self)

    def retrieve(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """
        Get a specific `Order` by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    def list(
        self,
        account_id: str,
        *,
        chain_id: Chain | NotGiven = NOT_GIVEN,
        order_transaction_hash: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderListResponse:
        """Get a list of all `Orders` under the `Account`.

        Optionally `Orders` can be
        filtered by chain ID or transaction hash.

        Args:
          chain_id: CAIP-2 formatted chain ID of the blockchain the `Order` was made on.

          order_transaction_hash: Transaction hash of the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/orders",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "chain_id": chain_id,
                        "order_transaction_hash": order_transaction_hash,
                        "page": page,
                        "page_size": page_size,
                    },
                    order_list_params.OrderListParams,
                ),
            ),
            cast_to=OrderListResponse,
        )

    def cancel(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """Cancel an `Order` by its ID.

        Note that this requires the `Order` ID, not the
        `OrderRequest` ID. Once you submit a cancellation request, it cannot be undone.
        Be advised that orders with a status of PENDING_FILL, PENDING_ESCROW, FILLED,
        REJECTED, or CANCELLED cannot be cancelled.

        `Order` cancellation is not guaranteed nor is it immediate. The `Order` may
        still be executed if the cancellation request is not received in time.

        Check the status using the "Get Order by ID" endpoint to confirm whether the
        `Order` has been cancelled.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    def get_fulfillments(
        self,
        order_id: str,
        *,
        account_id: str,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderGetFulfillmentsResponse:
        """
        Get `OrderFulfillments` for a specific `Order`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/fulfillments",
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
                    order_get_fulfillments_params.OrderGetFulfillmentsParams,
                ),
            ),
            cast_to=OrderGetFulfillmentsResponse,
        )


class AsyncOrdersResource(AsyncAPIResource):
    @cached_property
    def stocks(self) -> AsyncStocksResource:
        return AsyncStocksResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOrdersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrdersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrdersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return AsyncOrdersResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """
        Get a specific `Order` by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    async def list(
        self,
        account_id: str,
        *,
        chain_id: Chain | NotGiven = NOT_GIVEN,
        order_transaction_hash: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderListResponse:
        """Get a list of all `Orders` under the `Account`.

        Optionally `Orders` can be
        filtered by chain ID or transaction hash.

        Args:
          chain_id: CAIP-2 formatted chain ID of the blockchain the `Order` was made on.

          order_transaction_hash: Transaction hash of the `Order`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/orders",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "chain_id": chain_id,
                        "order_transaction_hash": order_transaction_hash,
                        "page": page,
                        "page_size": page_size,
                    },
                    order_list_params.OrderListParams,
                ),
            ),
            cast_to=OrderListResponse,
        )

    async def cancel(
        self,
        order_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """Cancel an `Order` by its ID.

        Note that this requires the `Order` ID, not the
        `OrderRequest` ID. Once you submit a cancellation request, it cannot be undone.
        Be advised that orders with a status of PENDING_FILL, PENDING_ESCROW, FILLED,
        REJECTED, or CANCELLED cannot be cancelled.

        `Order` cancellation is not guaranteed nor is it immediate. The `Order` may
        still be executed if the cancellation request is not received in time.

        Check the status using the "Get Order by ID" endpoint to confirm whether the
        `Order` has been cancelled.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )

    async def get_fulfillments(
        self,
        order_id: str,
        *,
        account_id: str,
        page: int | NotGiven = NOT_GIVEN,
        page_size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderGetFulfillmentsResponse:
        """
        Get `OrderFulfillments` for a specific `Order`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return await self._get(
            f"/api/v2/accounts/{account_id}/orders/{order_id}/fulfillments",
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
                    order_get_fulfillments_params.OrderGetFulfillmentsParams,
                ),
            ),
            cast_to=OrderGetFulfillmentsResponse,
        )


class OrdersResourceWithRawResponse:
    def __init__(self, orders: OrdersResource) -> None:
        self._orders = orders

        self.retrieve = to_raw_response_wrapper(
            orders.retrieve,
        )
        self.list = to_raw_response_wrapper(
            orders.list,
        )
        self.cancel = to_raw_response_wrapper(
            orders.cancel,
        )
        self.get_fulfillments = to_raw_response_wrapper(
            orders.get_fulfillments,
        )

    @cached_property
    def stocks(self) -> StocksResourceWithRawResponse:
        return StocksResourceWithRawResponse(self._orders.stocks)


class AsyncOrdersResourceWithRawResponse:
    def __init__(self, orders: AsyncOrdersResource) -> None:
        self._orders = orders

        self.retrieve = async_to_raw_response_wrapper(
            orders.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            orders.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            orders.cancel,
        )
        self.get_fulfillments = async_to_raw_response_wrapper(
            orders.get_fulfillments,
        )

    @cached_property
    def stocks(self) -> AsyncStocksResourceWithRawResponse:
        return AsyncStocksResourceWithRawResponse(self._orders.stocks)


class OrdersResourceWithStreamingResponse:
    def __init__(self, orders: OrdersResource) -> None:
        self._orders = orders

        self.retrieve = to_streamed_response_wrapper(
            orders.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            orders.list,
        )
        self.cancel = to_streamed_response_wrapper(
            orders.cancel,
        )
        self.get_fulfillments = to_streamed_response_wrapper(
            orders.get_fulfillments,
        )

    @cached_property
    def stocks(self) -> StocksResourceWithStreamingResponse:
        return StocksResourceWithStreamingResponse(self._orders.stocks)


class AsyncOrdersResourceWithStreamingResponse:
    def __init__(self, orders: AsyncOrdersResource) -> None:
        self._orders = orders

        self.retrieve = async_to_streamed_response_wrapper(
            orders.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            orders.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            orders.cancel,
        )
        self.get_fulfillments = async_to_streamed_response_wrapper(
            orders.get_fulfillments,
        )

    @cached_property
    def stocks(self) -> AsyncStocksResourceWithStreamingResponse:
        return AsyncStocksResourceWithStreamingResponse(self._orders.stocks)
