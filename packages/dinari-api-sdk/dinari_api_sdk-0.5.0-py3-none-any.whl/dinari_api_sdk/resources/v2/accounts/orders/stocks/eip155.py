# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ......_types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ......_utils import maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......types.v2 import Chain
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......_base_client import make_request_options
from ......types.v2.chain import Chain
from ......types.v2.accounts import OrderTif, OrderSide, OrderType
from ......types.v2.accounts.order_tif import OrderTif
from ......types.v2.accounts.order_side import OrderSide
from ......types.v2.accounts.order_type import OrderType
from ......types.v2.accounts.orders.stocks import eip155_get_fee_quote_params, eip155_prepare_order_params
from ......types.v2.accounts.orders.stocks.eip155_get_fee_quote_response import Eip155GetFeeQuoteResponse
from ......types.v2.accounts.orders.stocks.eip155_prepare_order_response import Eip155PrepareOrderResponse

__all__ = ["Eip155Resource", "AsyncEip155Resource"]


class Eip155Resource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> Eip155ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return Eip155ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> Eip155ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return Eip155ResourceWithStreamingResponse(self)

    def get_fee_quote(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        payment_token: str,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Eip155GetFeeQuoteResponse:
        """
        Get fee quote data for an `Order` to be placed on Dinari's EVM smart contracts.

        Dinari's EVM smart contracts require a fee quote to be provided when placing an
        `Order`. Use this method to retrieve the quote.

        The `order_fee_contract_object` property contains the opaque fee quote structure
        to be used.

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          payment_token: Address of payment token.

          stock_id: The ID of the `Stock` for which the `Order` is being placed.

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/orders/stocks/eip155/fee_quote",
            body=maybe_transform(
                {
                    "chain_id": chain_id,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "payment_token": payment_token,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "limit_price": limit_price,
                    "payment_token_quantity": payment_token_quantity,
                },
                eip155_get_fee_quote_params.Eip155GetFeeQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Eip155GetFeeQuoteResponse,
        )

    def prepare_order(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        payment_token: str,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Eip155PrepareOrderResponse:
        """
        Create a set of transactions to create an `Order` using Dinari's EVM smart
        contracts.

        This is a convenience method to prepare the transactions needed to create an
        `Order` using Dinari's EVM smart contracts. Once signed, the transactions can be
        sent to the EVM network to create the order. Note that the fee quote is already
        included in the transactions, so no additional fee quote lookup is needed.

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          payment_token: Address of payment token.

          stock_id: The ID of the `Stock` for which the `Order` is being placed.

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/orders/stocks/eip155/prepare",
            body=maybe_transform(
                {
                    "chain_id": chain_id,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "payment_token": payment_token,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "limit_price": limit_price,
                    "payment_token_quantity": payment_token_quantity,
                },
                eip155_prepare_order_params.Eip155PrepareOrderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Eip155PrepareOrderResponse,
        )


class AsyncEip155Resource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEip155ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEip155ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEip155ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return AsyncEip155ResourceWithStreamingResponse(self)

    async def get_fee_quote(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        payment_token: str,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Eip155GetFeeQuoteResponse:
        """
        Get fee quote data for an `Order` to be placed on Dinari's EVM smart contracts.

        Dinari's EVM smart contracts require a fee quote to be provided when placing an
        `Order`. Use this method to retrieve the quote.

        The `order_fee_contract_object` property contains the opaque fee quote structure
        to be used.

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          payment_token: Address of payment token.

          stock_id: The ID of the `Stock` for which the `Order` is being placed.

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/orders/stocks/eip155/fee_quote",
            body=await async_maybe_transform(
                {
                    "chain_id": chain_id,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "payment_token": payment_token,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "limit_price": limit_price,
                    "payment_token_quantity": payment_token_quantity,
                },
                eip155_get_fee_quote_params.Eip155GetFeeQuoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Eip155GetFeeQuoteResponse,
        )

    async def prepare_order(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        payment_token: str,
        stock_id: str,
        asset_token_quantity: float | NotGiven = NOT_GIVEN,
        limit_price: float | NotGiven = NOT_GIVEN,
        payment_token_quantity: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Eip155PrepareOrderResponse:
        """
        Create a set of transactions to create an `Order` using Dinari's EVM smart
        contracts.

        This is a convenience method to prepare the transactions needed to create an
        `Order` using Dinari's EVM smart contracts. Once signed, the transactions can be
        sent to the EVM network to create the order. Note that the fee quote is already
        included in the transactions, so no additional fee quote lookup is needed.

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          payment_token: Address of payment token.

          stock_id: The ID of the `Stock` for which the `Order` is being placed.

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/orders/stocks/eip155/prepare",
            body=await async_maybe_transform(
                {
                    "chain_id": chain_id,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "payment_token": payment_token,
                    "stock_id": stock_id,
                    "asset_token_quantity": asset_token_quantity,
                    "limit_price": limit_price,
                    "payment_token_quantity": payment_token_quantity,
                },
                eip155_prepare_order_params.Eip155PrepareOrderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Eip155PrepareOrderResponse,
        )


class Eip155ResourceWithRawResponse:
    def __init__(self, eip155: Eip155Resource) -> None:
        self._eip155 = eip155

        self.get_fee_quote = to_raw_response_wrapper(
            eip155.get_fee_quote,
        )
        self.prepare_order = to_raw_response_wrapper(
            eip155.prepare_order,
        )


class AsyncEip155ResourceWithRawResponse:
    def __init__(self, eip155: AsyncEip155Resource) -> None:
        self._eip155 = eip155

        self.get_fee_quote = async_to_raw_response_wrapper(
            eip155.get_fee_quote,
        )
        self.prepare_order = async_to_raw_response_wrapper(
            eip155.prepare_order,
        )


class Eip155ResourceWithStreamingResponse:
    def __init__(self, eip155: Eip155Resource) -> None:
        self._eip155 = eip155

        self.get_fee_quote = to_streamed_response_wrapper(
            eip155.get_fee_quote,
        )
        self.prepare_order = to_streamed_response_wrapper(
            eip155.prepare_order,
        )


class AsyncEip155ResourceWithStreamingResponse:
    def __init__(self, eip155: AsyncEip155Resource) -> None:
        self._eip155 = eip155

        self.get_fee_quote = async_to_streamed_response_wrapper(
            eip155.get_fee_quote,
        )
        self.prepare_order = async_to_streamed_response_wrapper(
            eip155.prepare_order,
        )
