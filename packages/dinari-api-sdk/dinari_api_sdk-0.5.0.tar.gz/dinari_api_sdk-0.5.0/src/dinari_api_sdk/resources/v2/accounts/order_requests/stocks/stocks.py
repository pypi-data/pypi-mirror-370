# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .eip155 import (
    Eip155Resource,
    AsyncEip155Resource,
    Eip155ResourceWithRawResponse,
    AsyncEip155ResourceWithRawResponse,
    Eip155ResourceWithStreamingResponse,
    AsyncEip155ResourceWithStreamingResponse,
)
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource

__all__ = ["StocksResource", "AsyncStocksResource"]


class StocksResource(SyncAPIResource):
    @cached_property
    def eip155(self) -> Eip155Resource:
        return Eip155Resource(self._client)

    @cached_property
    def with_raw_response(self) -> StocksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return StocksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StocksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return StocksResourceWithStreamingResponse(self)


class AsyncStocksResource(AsyncAPIResource):
    @cached_property
    def eip155(self) -> AsyncEip155Resource:
        return AsyncEip155Resource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncStocksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStocksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStocksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return AsyncStocksResourceWithStreamingResponse(self)


class StocksResourceWithRawResponse:
    def __init__(self, stocks: StocksResource) -> None:
        self._stocks = stocks

    @cached_property
    def eip155(self) -> Eip155ResourceWithRawResponse:
        return Eip155ResourceWithRawResponse(self._stocks.eip155)


class AsyncStocksResourceWithRawResponse:
    def __init__(self, stocks: AsyncStocksResource) -> None:
        self._stocks = stocks

    @cached_property
    def eip155(self) -> AsyncEip155ResourceWithRawResponse:
        return AsyncEip155ResourceWithRawResponse(self._stocks.eip155)


class StocksResourceWithStreamingResponse:
    def __init__(self, stocks: StocksResource) -> None:
        self._stocks = stocks

    @cached_property
    def eip155(self) -> Eip155ResourceWithStreamingResponse:
        return Eip155ResourceWithStreamingResponse(self._stocks.eip155)


class AsyncStocksResourceWithStreamingResponse:
    def __init__(self, stocks: AsyncStocksResource) -> None:
        self._stocks = stocks

    @cached_property
    def eip155(self) -> AsyncEip155ResourceWithStreamingResponse:
        return AsyncEip155ResourceWithStreamingResponse(self._stocks.eip155)
