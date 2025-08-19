# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from payi import Payi, AsyncPayi
from payi.types import CategoryResourceResponse
from payi._utils import parse_datetime
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFixedCostResources:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Payi) -> None:
        fixed_cost_resource = client.categories.fixed_cost_resources.create(
            resource="resource",
            category="category",
            units=["string"],
        )
        assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Payi) -> None:
        fixed_cost_resource = client.categories.fixed_cost_resources.create(
            resource="resource",
            category="category",
            units=["string"],
            cost_per_hour=0,
            start_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Payi) -> None:
        response = client.categories.fixed_cost_resources.with_raw_response.create(
            resource="resource",
            category="category",
            units=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fixed_cost_resource = response.parse()
        assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Payi) -> None:
        with client.categories.fixed_cost_resources.with_streaming_response.create(
            resource="resource",
            category="category",
            units=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fixed_cost_resource = response.parse()
            assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Payi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `category` but received ''"):
            client.categories.fixed_cost_resources.with_raw_response.create(
                resource="resource",
                category="",
                units=["string"],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource` but received ''"):
            client.categories.fixed_cost_resources.with_raw_response.create(
                resource="",
                category="category",
                units=["string"],
            )


class TestAsyncFixedCostResources:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncPayi) -> None:
        fixed_cost_resource = await async_client.categories.fixed_cost_resources.create(
            resource="resource",
            category="category",
            units=["string"],
        )
        assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncPayi) -> None:
        fixed_cost_resource = await async_client.categories.fixed_cost_resources.create(
            resource="resource",
            category="category",
            units=["string"],
            cost_per_hour=0,
            start_timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncPayi) -> None:
        response = await async_client.categories.fixed_cost_resources.with_raw_response.create(
            resource="resource",
            category="category",
            units=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fixed_cost_resource = await response.parse()
        assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncPayi) -> None:
        async with async_client.categories.fixed_cost_resources.with_streaming_response.create(
            resource="resource",
            category="category",
            units=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fixed_cost_resource = await response.parse()
            assert_matches_type(CategoryResourceResponse, fixed_cost_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncPayi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `category` but received ''"):
            await async_client.categories.fixed_cost_resources.with_raw_response.create(
                resource="resource",
                category="",
                units=["string"],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `resource` but received ''"):
            await async_client.categories.fixed_cost_resources.with_raw_response.create(
                resource="",
                category="category",
                units=["string"],
            )
