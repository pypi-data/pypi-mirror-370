# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from dinari_api_sdk import Dinari, AsyncDinari
from dinari_api_sdk._utils import parse_date
from dinari_api_sdk.types.v2.entities import KYCInfo, KYCCreateManagedCheckResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestKYC:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Dinari) -> None:
        kyc = client.v2.entities.kyc.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Dinari) -> None:
        response = client.v2.entities.kyc.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kyc = response.parse()
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Dinari) -> None:
        with client.v2.entities.kyc.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kyc = response.parse()
            assert_matches_type(KYCInfo, kyc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Dinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.v2.entities.kyc.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_managed_check(self, client: Dinari) -> None:
        kyc = client.v2.entities.kyc.create_managed_check(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(KYCCreateManagedCheckResponse, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_managed_check(self, client: Dinari) -> None:
        response = client.v2.entities.kyc.with_raw_response.create_managed_check(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kyc = response.parse()
        assert_matches_type(KYCCreateManagedCheckResponse, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_managed_check(self, client: Dinari) -> None:
        with client.v2.entities.kyc.with_streaming_response.create_managed_check(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kyc = response.parse()
            assert_matches_type(KYCCreateManagedCheckResponse, kyc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_managed_check(self, client: Dinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.v2.entities.kyc.with_raw_response.create_managed_check(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit(self, client: Dinari) -> None:
        kyc = client.v2.entities.kyc.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
            },
            provider_name="x",
        )
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit_with_all_params(self, client: Dinari) -> None:
        kyc = client.v2.entities.kyc.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
                "address_city": "San Francisco",
                "address_postal_code": "94111",
                "address_street_1": "123 Main St.",
                "address_street_2": "Apt. 123",
                "address_subdivision": "California",
                "birth_date": parse_date("2019-12-27"),
                "email": "johndoe@website.com",
                "first_name": "John",
                "middle_name": "x",
                "tax_id_number": "12-3456789",
            },
            provider_name="x",
        )
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_submit(self, client: Dinari) -> None:
        response = client.v2.entities.kyc.with_raw_response.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
            },
            provider_name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kyc = response.parse()
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_submit(self, client: Dinari) -> None:
        with client.v2.entities.kyc.with_streaming_response.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
            },
            provider_name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kyc = response.parse()
            assert_matches_type(KYCInfo, kyc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_submit(self, client: Dinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.v2.entities.kyc.with_raw_response.submit(
                entity_id="",
                data={
                    "address_country_code": "SG",
                    "country_code": "SG",
                    "last_name": "Doe",
                },
                provider_name="x",
            )


class TestAsyncKYC:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncDinari) -> None:
        kyc = await async_client.v2.entities.kyc.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncDinari) -> None:
        response = await async_client.v2.entities.kyc.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kyc = await response.parse()
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncDinari) -> None:
        async with async_client.v2.entities.kyc.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kyc = await response.parse()
            assert_matches_type(KYCInfo, kyc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncDinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.v2.entities.kyc.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_managed_check(self, async_client: AsyncDinari) -> None:
        kyc = await async_client.v2.entities.kyc.create_managed_check(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(KYCCreateManagedCheckResponse, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_managed_check(self, async_client: AsyncDinari) -> None:
        response = await async_client.v2.entities.kyc.with_raw_response.create_managed_check(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kyc = await response.parse()
        assert_matches_type(KYCCreateManagedCheckResponse, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_managed_check(self, async_client: AsyncDinari) -> None:
        async with async_client.v2.entities.kyc.with_streaming_response.create_managed_check(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kyc = await response.parse()
            assert_matches_type(KYCCreateManagedCheckResponse, kyc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_managed_check(self, async_client: AsyncDinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.v2.entities.kyc.with_raw_response.create_managed_check(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit(self, async_client: AsyncDinari) -> None:
        kyc = await async_client.v2.entities.kyc.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
            },
            provider_name="x",
        )
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncDinari) -> None:
        kyc = await async_client.v2.entities.kyc.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
                "address_city": "San Francisco",
                "address_postal_code": "94111",
                "address_street_1": "123 Main St.",
                "address_street_2": "Apt. 123",
                "address_subdivision": "California",
                "birth_date": parse_date("2019-12-27"),
                "email": "johndoe@website.com",
                "first_name": "John",
                "middle_name": "x",
                "tax_id_number": "12-3456789",
            },
            provider_name="x",
        )
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncDinari) -> None:
        response = await async_client.v2.entities.kyc.with_raw_response.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
            },
            provider_name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        kyc = await response.parse()
        assert_matches_type(KYCInfo, kyc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncDinari) -> None:
        async with async_client.v2.entities.kyc.with_streaming_response.submit(
            entity_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            data={
                "address_country_code": "SG",
                "country_code": "SG",
                "last_name": "Doe",
            },
            provider_name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            kyc = await response.parse()
            assert_matches_type(KYCInfo, kyc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_submit(self, async_client: AsyncDinari) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.v2.entities.kyc.with_raw_response.submit(
                entity_id="",
                data={
                    "address_country_code": "SG",
                    "country_code": "SG",
                    "last_name": "Doe",
                },
                provider_name="x",
            )
