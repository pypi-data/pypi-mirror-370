# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.categories import fixed_cost_resource_create_params
from ...types.category_resource_response import CategoryResourceResponse

__all__ = ["FixedCostResourcesResource", "AsyncFixedCostResourcesResource"]


class FixedCostResourcesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FixedCostResourcesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Pay-i/pay-i-python#accessing-raw-response-data-eg-headers
        """
        return FixedCostResourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FixedCostResourcesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Pay-i/pay-i-python#with_streaming_response
        """
        return FixedCostResourcesResourceWithStreamingResponse(self)

    def create(
        self,
        resource: str,
        *,
        category: str,
        units: List[str],
        cost_per_hour: float | NotGiven = NOT_GIVEN,
        start_timestamp: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CategoryResourceResponse:
        """
        Create a fixed cost resource

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not category:
            raise ValueError(f"Expected a non-empty value for `category` but received {category!r}")
        if not resource:
            raise ValueError(f"Expected a non-empty value for `resource` but received {resource!r}")
        return self._post(
            f"/api/v1/categories/{category}/fixed_cost_resources/{resource}",
            body=maybe_transform(
                {
                    "units": units,
                    "cost_per_hour": cost_per_hour,
                    "start_timestamp": start_timestamp,
                },
                fixed_cost_resource_create_params.FixedCostResourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CategoryResourceResponse,
        )


class AsyncFixedCostResourcesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFixedCostResourcesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Pay-i/pay-i-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFixedCostResourcesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFixedCostResourcesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Pay-i/pay-i-python#with_streaming_response
        """
        return AsyncFixedCostResourcesResourceWithStreamingResponse(self)

    async def create(
        self,
        resource: str,
        *,
        category: str,
        units: List[str],
        cost_per_hour: float | NotGiven = NOT_GIVEN,
        start_timestamp: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CategoryResourceResponse:
        """
        Create a fixed cost resource

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not category:
            raise ValueError(f"Expected a non-empty value for `category` but received {category!r}")
        if not resource:
            raise ValueError(f"Expected a non-empty value for `resource` but received {resource!r}")
        return await self._post(
            f"/api/v1/categories/{category}/fixed_cost_resources/{resource}",
            body=await async_maybe_transform(
                {
                    "units": units,
                    "cost_per_hour": cost_per_hour,
                    "start_timestamp": start_timestamp,
                },
                fixed_cost_resource_create_params.FixedCostResourceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CategoryResourceResponse,
        )


class FixedCostResourcesResourceWithRawResponse:
    def __init__(self, fixed_cost_resources: FixedCostResourcesResource) -> None:
        self._fixed_cost_resources = fixed_cost_resources

        self.create = to_raw_response_wrapper(
            fixed_cost_resources.create,
        )


class AsyncFixedCostResourcesResourceWithRawResponse:
    def __init__(self, fixed_cost_resources: AsyncFixedCostResourcesResource) -> None:
        self._fixed_cost_resources = fixed_cost_resources

        self.create = async_to_raw_response_wrapper(
            fixed_cost_resources.create,
        )


class FixedCostResourcesResourceWithStreamingResponse:
    def __init__(self, fixed_cost_resources: FixedCostResourcesResource) -> None:
        self._fixed_cost_resources = fixed_cost_resources

        self.create = to_streamed_response_wrapper(
            fixed_cost_resources.create,
        )


class AsyncFixedCostResourcesResourceWithStreamingResponse:
    def __init__(self, fixed_cost_resources: AsyncFixedCostResourcesResource) -> None:
        self._fixed_cost_resources = fixed_cost_resources

        self.create = async_to_streamed_response_wrapper(
            fixed_cost_resources.create,
        )
