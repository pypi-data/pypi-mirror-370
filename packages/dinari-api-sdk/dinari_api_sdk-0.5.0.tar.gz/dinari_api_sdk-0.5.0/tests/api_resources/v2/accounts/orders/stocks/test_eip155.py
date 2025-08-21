# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from dinari_api_sdk import Dinari, AsyncDinari
from dinari_api_sdk.types.v2.accounts.orders.stocks import (
    Eip155GetFeeQuoteResponse,
    Eip155PrepareOrderResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEip155:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_fee_quote(self, client: Dinari) -> None:
        eip155 = client.v2.accounts.orders.stocks.eip155.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_fee_quote_with_all_params(self, client: Dinari) -> None:
        eip155 = client.v2.accounts.orders.stocks.eip155.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            asset_token_quantity=0,
            limit_price=0,
            payment_token_quantity=0,
        )
        assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_fee_quote(self, client: Dinari) -> None:
        response = client.v2.accounts.orders.stocks.eip155.with_raw_response.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eip155 = response.parse()
        assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_fee_quote(self, client: Dinari) -> None:
        with client.v2.accounts.orders.stocks.eip155.with_streaming_response.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eip155 = response.parse()
            assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_fee_quote(self, client: Dinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.v2.accounts.orders.stocks.eip155.with_raw_response.get_fee_quote(
                account_id="",
                chain_id="eip155:1",
                order_side="BUY",
                order_tif="DAY",
                order_type="MARKET",
                payment_token="payment_token",
                stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_prepare_order(self, client: Dinari) -> None:
        eip155 = client.v2.accounts.orders.stocks.eip155.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_prepare_order_with_all_params(self, client: Dinari) -> None:
        eip155 = client.v2.accounts.orders.stocks.eip155.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            asset_token_quantity=0,
            limit_price=0,
            payment_token_quantity=0,
        )
        assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_prepare_order(self, client: Dinari) -> None:
        response = client.v2.accounts.orders.stocks.eip155.with_raw_response.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eip155 = response.parse()
        assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_prepare_order(self, client: Dinari) -> None:
        with client.v2.accounts.orders.stocks.eip155.with_streaming_response.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eip155 = response.parse()
            assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_prepare_order(self, client: Dinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.v2.accounts.orders.stocks.eip155.with_raw_response.prepare_order(
                account_id="",
                chain_id="eip155:1",
                order_side="BUY",
                order_tif="DAY",
                order_type="MARKET",
                payment_token="payment_token",
                stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncEip155:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_fee_quote(self, async_client: AsyncDinari) -> None:
        eip155 = await async_client.v2.accounts.orders.stocks.eip155.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_fee_quote_with_all_params(self, async_client: AsyncDinari) -> None:
        eip155 = await async_client.v2.accounts.orders.stocks.eip155.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            asset_token_quantity=0,
            limit_price=0,
            payment_token_quantity=0,
        )
        assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_fee_quote(self, async_client: AsyncDinari) -> None:
        response = await async_client.v2.accounts.orders.stocks.eip155.with_raw_response.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eip155 = await response.parse()
        assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_fee_quote(self, async_client: AsyncDinari) -> None:
        async with async_client.v2.accounts.orders.stocks.eip155.with_streaming_response.get_fee_quote(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eip155 = await response.parse()
            assert_matches_type(Eip155GetFeeQuoteResponse, eip155, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_fee_quote(self, async_client: AsyncDinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.v2.accounts.orders.stocks.eip155.with_raw_response.get_fee_quote(
                account_id="",
                chain_id="eip155:1",
                order_side="BUY",
                order_tif="DAY",
                order_type="MARKET",
                payment_token="payment_token",
                stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_prepare_order(self, async_client: AsyncDinari) -> None:
        eip155 = await async_client.v2.accounts.orders.stocks.eip155.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_prepare_order_with_all_params(self, async_client: AsyncDinari) -> None:
        eip155 = await async_client.v2.accounts.orders.stocks.eip155.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            asset_token_quantity=0,
            limit_price=0,
            payment_token_quantity=0,
        )
        assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_prepare_order(self, async_client: AsyncDinari) -> None:
        response = await async_client.v2.accounts.orders.stocks.eip155.with_raw_response.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eip155 = await response.parse()
        assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_prepare_order(self, async_client: AsyncDinari) -> None:
        async with async_client.v2.accounts.orders.stocks.eip155.with_streaming_response.prepare_order(
            account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            chain_id="eip155:1",
            order_side="BUY",
            order_tif="DAY",
            order_type="MARKET",
            payment_token="payment_token",
            stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eip155 = await response.parse()
            assert_matches_type(Eip155PrepareOrderResponse, eip155, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_prepare_order(self, async_client: AsyncDinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.v2.accounts.orders.stocks.eip155.with_raw_response.prepare_order(
                account_id="",
                chain_id="eip155:1",
                order_side="BUY",
                order_tif="DAY",
                order_type="MARKET",
                payment_token="payment_token",
                stock_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
