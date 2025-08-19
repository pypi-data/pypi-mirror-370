# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from datetime import datetime

import httpx

from payi._utils._utils import is_given

from ..types import ingest_units_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.ingest_response import IngestResponse
from ..types.ingest_event_param import IngestEventParam
from ..types.bulk_ingest_response import BulkIngestResponse
from ..types.shared_params.ingest_units import IngestUnits
from ..types.pay_i_common_models_api_router_header_info_param import PayICommonModelsAPIRouterHeaderInfoParam

__all__ = ["IngestResource", "AsyncIngestResource"]


class IngestResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IngestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Pay-i/pay-i-python#accessing-raw-response-data-eg-headers
        """
        return IngestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IngestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Pay-i/pay-i-python#with_streaming_response
        """
        return IngestResourceWithStreamingResponse(self)

    def bulk(
        self,
        *,
        events: Iterable[IngestEventParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkIngestResponse:
        """
        Bulk Ingest

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/ingest/bulk",
            body=maybe_transform(events, Iterable[IngestEventParam]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkIngestResponse,
        )

    def units(
        self,
        *,
        category: str,
        units: Dict[str, IngestUnits],
        end_to_end_latency_ms: Optional[int] | NotGiven = NOT_GIVEN,
        event_timestamp: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        http_status_code: Optional[int] | NotGiven = NOT_GIVEN,
        properties: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        provider_request_headers: Optional[Iterable[PayICommonModelsAPIRouterHeaderInfoParam]] | NotGiven = NOT_GIVEN,
        provider_request_json: Optional[str] | NotGiven = NOT_GIVEN,
        provider_request_reasoning_json: Optional[str] | NotGiven = NOT_GIVEN,
        provider_response_function_calls: Optional[Iterable[ingest_units_params.ProviderResponseFunctionCall]]
        | NotGiven = NOT_GIVEN,
        provider_response_headers: Optional[Iterable[PayICommonModelsAPIRouterHeaderInfoParam]] | NotGiven = NOT_GIVEN,
        provider_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        provider_response_json: Union[str, List[str], None] | NotGiven = NOT_GIVEN,
        provider_uri: Optional[str] | NotGiven = NOT_GIVEN,
        resource: Optional[str] | NotGiven = NOT_GIVEN,
        time_to_first_completion_token_ms: Optional[int] | NotGiven = NOT_GIVEN,
        time_to_first_token_ms: Optional[int] | NotGiven = NOT_GIVEN,
        use_case_properties: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        limit_ids: Optional[list[str]] | NotGiven = NOT_GIVEN,
        request_tags: Optional[list[str]] | NotGiven = NOT_GIVEN,
        use_case_id: Optional[str] | NotGiven = NOT_GIVEN,
        use_case_name: Optional[str] | NotGiven = NOT_GIVEN,
        use_case_step: Optional[str] | NotGiven = NOT_GIVEN,
        use_case_version: Optional[int] | NotGiven = NOT_GIVEN,
        user_id: Optional[str] | NotGiven = NOT_GIVEN,
        resource_scope: Optional[str] | NotGiven = NOT_GIVEN,
        account_name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IngestResponse:
        """
        Ingest an Event

        Args:
          category (str): The name of the category

          resource (str): The name of the resource

          input (int): The number of input units

          output (int): The number of output units

          event_timestamp: (str, datetime, None): The timestamp of the event

          limit_ids (list[str], optional): The limit IDs to associate with the request

          properties (Dict[str, str], optional): Properties to associate with the request

          request_tags (list[str], optional): The request tags to associate with the request

          use_case_name (str, optional): The use case name

          use_case_id (str, optional): The use case instance id

          use_case_step (str, optional): The use case step

          use_case_version (int, optional): The use case instance version

          use_case_properties (Dict[str, str], optional): The use case properties

          user_id (str, optional): The user id
          
          resource_scope(str, optional): The scope of the resource

          account_name (str, optional): The account name

          extra_headers (Dict[str, str], optional): Additional headers for the request. Defaults to None.

          extra_query (Dict[str, str], optional): Additional query parameters. Defaults to None.

          extra_body (Dict[str, Any], optional): Additional body parameters. Defaults to None.

          timeout (Union[float, None], optional): The timeout for the request in seconds. Defaults to None.
        """
        valid_ids_str: str | NotGiven = NOT_GIVEN
        _valid_tags_str: str | NotGiven = NOT_GIVEN
        use_case_version_str: str | NotGiven = NOT_GIVEN

        if limit_ids is None or isinstance(limit_ids, NotGiven):
            valid_ids_str = NOT_GIVEN
        elif not isinstance(limit_ids, list):  # type: ignore
            raise TypeError("limit_ids must be a list")
        else:
            # Proceed with the list comprehension if limit_ids is not NotGiven
            valid_ids = [id.strip() for id in limit_ids if id.strip()]
            valid_ids_str = ",".join(valid_ids) if valid_ids else NOT_GIVEN

        if request_tags is None or isinstance(request_tags, NotGiven):
            _valid_tags_str = NOT_GIVEN
        elif not isinstance(request_tags, list):  # type: ignore
            raise TypeError("request_tags must be a list")
        else:
            # Proceed with the list comprehension if request_tags is not NotGiven
            valid_tags = [tag.strip() for tag in request_tags if tag.strip()]
            _valid_tags_str = ",".join(valid_tags) if valid_tags else NOT_GIVEN

        if use_case_name is None or isinstance(use_case_name, NotGiven):
            use_case_name = NOT_GIVEN

        if use_case_step is None or isinstance(use_case_step, NotGiven):
            use_case_step = NOT_GIVEN
        
        if use_case_id is None or isinstance(use_case_id, NotGiven):
            use_case_id = NOT_GIVEN
        
        if use_case_version is None or isinstance(use_case_version, NotGiven):
            use_case_version_str = NOT_GIVEN
        else:
            use_case_version_str = str(use_case_version)

        if user_id is None or isinstance(user_id, NotGiven):
            user_id = NOT_GIVEN

        if resource_scope is None or isinstance(resource_scope, NotGiven):
            resource_scope = NOT_GIVEN

        if account_name is None or isinstance(account_name, NotGiven):
            account_name = NOT_GIVEN

        extra_headers = {
            **strip_not_given(
                {
                    "xProxy-Limit-IDs": valid_ids_str,
                    "xProxy-Request-Tags": NOT_GIVEN, # _valid_tags_str
                    "xProxy-UseCase-ID": use_case_id,
                    "xProxy-UseCase-Name": use_case_name,
                    "xProxy-UseCase-Step": use_case_step,
                    "xProxy-UseCase-Version": use_case_version_str
                    if is_given(use_case_version)
                    else NOT_GIVEN,
                    "xProxy-User-ID": user_id,
                    "xProxy-Resource-Scope": resource_scope,
                    "xProxy-Account-Name": account_name,
                }
            ),
            **(extra_headers or {}),
        }

        return self._post(
            "/api/v1/ingest",
            body=maybe_transform(
                {
                    "category": category,
                    "units": units,
                    "end_to_end_latency_ms": end_to_end_latency_ms,
                    "event_timestamp": event_timestamp,
                    "http_status_code": http_status_code,
                    "properties": properties,
                    "provider_request_headers": provider_request_headers,
                    "provider_request_json": provider_request_json,
                    "provider_request_reasoning_json": provider_request_reasoning_json,
                    "provider_response_function_calls": provider_response_function_calls,
                    "provider_response_headers": provider_response_headers,
                    "provider_response_id": provider_response_id,
                    "provider_response_json": provider_response_json,
                    "provider_uri": provider_uri,
                    "resource": resource,
                    "time_to_first_completion_token_ms": time_to_first_completion_token_ms,
                    "time_to_first_token_ms": time_to_first_token_ms,
                    "use_case_properties": use_case_properties,
                },
                ingest_units_params.IngestUnitsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IngestResponse,
        )


class AsyncIngestResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIngestResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Pay-i/pay-i-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIngestResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIngestResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Pay-i/pay-i-python#with_streaming_response
        """
        return AsyncIngestResourceWithStreamingResponse(self)

    async def bulk(
        self,
        *,
        events: Iterable[IngestEventParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BulkIngestResponse:
        """
        Bulk Ingest

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/ingest/bulk",
            body=await async_maybe_transform(events, Iterable[IngestEventParam]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BulkIngestResponse,
        )

    async def units(
        self,
        *,
        category: str,
        units: Dict[str, IngestUnits],
        end_to_end_latency_ms: Optional[int] | NotGiven = NOT_GIVEN,
        event_timestamp: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        http_status_code: Optional[int] | NotGiven = NOT_GIVEN,
        properties: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        provider_request_headers: Optional[Iterable[PayICommonModelsAPIRouterHeaderInfoParam]] | NotGiven = NOT_GIVEN,
        provider_request_json: Optional[str] | NotGiven = NOT_GIVEN,
        provider_request_reasoning_json: Optional[str] | NotGiven = NOT_GIVEN,
        provider_response_function_calls: Optional[Iterable[ingest_units_params.ProviderResponseFunctionCall]]
        | NotGiven = NOT_GIVEN,
        provider_response_headers: Optional[Iterable[PayICommonModelsAPIRouterHeaderInfoParam]] | NotGiven = NOT_GIVEN,
        provider_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        provider_response_json: Union[str, List[str], None] | NotGiven = NOT_GIVEN,
        provider_uri: Optional[str] | NotGiven = NOT_GIVEN,
        resource: Optional[str] | NotGiven = NOT_GIVEN,
        time_to_first_completion_token_ms: Optional[int] | NotGiven = NOT_GIVEN,
        time_to_first_token_ms: Optional[int] | NotGiven = NOT_GIVEN,
        use_case_properties: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        limit_ids: Optional[list[str]] | NotGiven = NOT_GIVEN,
        request_tags: Optional[list[str]] | NotGiven = NOT_GIVEN,
        use_case_id: Optional[str] | NotGiven = NOT_GIVEN,
        use_case_name: Optional[str] | NotGiven = NOT_GIVEN,
        use_case_step: Optional[str] | NotGiven = NOT_GIVEN,
        use_case_version: Optional[int] | NotGiven = NOT_GIVEN,
        user_id: Optional[str] | NotGiven = NOT_GIVEN,
        resource_scope: Union[str, None] | NotGiven = NOT_GIVEN,
        account_name: Optional[str] | NotGiven = NOT_GIVEN,
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IngestResponse:
        """
        Ingest an Event

        Args:
          category (str): The name of the category

          resource (str): The name of the resource

          input (int): The number of input units

          output (int): The number of output units

          event_timestamp: (datetime, None): The timestamp of the event

          limit_ids (list[str], optional): The limit IDs to associate with the request 

          properties (Dict[str, str], optional): Properties to associate with the request 

          request_tags (list[str], optional): The request tags to associate with the request

          use_case_name (str, optional): The use case name

          use_case_step (str, optional): The use case step

          use_case_id (str, optional): The use case instance id

          use_case_version (int, optional): The use case instance version

          use_case_properties (Dict[str, str], optional): The use case properties

          user_id (str, optional): The user id
          
          resource_scope (str, optional): The scope of the resource

          account_name (str, optional): The account name

          extra_headers (Dict[str, str], optional): Additional headers for the request. Defaults to None.

          extra_query (Dict[str, str], optional): Additional query parameters. Defaults to None.

          extra_body (Dict[str, Any], optional): Additional body parameters. Defaults to None.

          timeout (Union[float, None], optional): The timeout for the request in seconds. Defaults to None.
        """
        valid_ids_str: str | NotGiven = NOT_GIVEN
        _valid_tags_str: str | NotGiven = NOT_GIVEN
        use_case_version_str: str | NotGiven = NOT_GIVEN

        if limit_ids is None or isinstance(limit_ids, NotGiven):
            valid_ids_str = NOT_GIVEN
        elif not isinstance(limit_ids, list):  # type: ignore
            raise TypeError("limit_ids must be a list")
        else:
            # Proceed with the list comprehension if limit_ids is not NotGiven
            valid_ids = [id.strip() for id in limit_ids if id.strip()]
            valid_ids_str = ",".join(valid_ids) if valid_ids else NOT_GIVEN

        if request_tags is None or isinstance(request_tags, NotGiven):
            _valid_tags_str = NOT_GIVEN
        elif not isinstance(request_tags, list):  # type: ignore
            raise TypeError("request_tags must be a list")
        else:
            # Proceed with the list comprehension if request_tags is not NotGiven
            valid_tags = [tag.strip() for tag in request_tags if tag.strip()]
            _valid_tags_str = ",".join(valid_tags) if valid_tags else NOT_GIVEN

        if use_case_name is None or isinstance(use_case_name, NotGiven):
            use_case_name = NOT_GIVEN
        
        if use_case_step is None or isinstance(use_case_step, NotGiven):
            use_case_step = NOT_GIVEN
        
        if use_case_id is None or isinstance(use_case_id, NotGiven):
            use_case_id = NOT_GIVEN

        if use_case_version is None or isinstance(use_case_version, NotGiven):
            use_case_version_str = NOT_GIVEN
        else:
            use_case_version_str = str(use_case_version)

        if user_id is None or isinstance(user_id, NotGiven):
            user_id = NOT_GIVEN

        if resource_scope is None or isinstance(resource_scope, NotGiven):
            resource_scope = NOT_GIVEN

        if account_name is None or isinstance(account_name, NotGiven):
            account_name = NOT_GIVEN

        extra_headers = {
            **strip_not_given(
                {
                    "xProxy-Account-Name": account_name,
                    "xProxy-Limit-IDs": valid_ids_str,
                    "xProxy-Request-Tags": NOT_GIVEN, # _valid_tags_str,
                    "xProxy-UseCase-ID": use_case_id,
                    "xProxy-UseCase-Name": use_case_name,
                    "xProxy-UseCase-Step": use_case_step,
                    "xProxy-UseCase-Version": use_case_version_str
                    if is_given(use_case_version)
                    else NOT_GIVEN,
                    "xProxy-User-ID": user_id,
                    "xProxy-Resource-Scope": resource_scope,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            "/api/v1/ingest",
            body=await async_maybe_transform(
                {
                    "category": category,
                    "units": units,
                    "end_to_end_latency_ms": end_to_end_latency_ms,
                    "event_timestamp": event_timestamp,
                    "http_status_code": http_status_code,
                    "properties": properties,
                    "provider_request_headers": provider_request_headers,
                    "provider_request_json": provider_request_json,
                    "provider_request_reasoning_json": provider_request_reasoning_json,
                    "provider_response_function_calls": provider_response_function_calls,
                    "provider_response_headers": provider_response_headers,
                    "provider_response_id": provider_response_id,
                    "provider_response_json": provider_response_json,
                    "provider_uri": provider_uri,
                    "resource": resource,
                    "time_to_first_completion_token_ms": time_to_first_completion_token_ms,
                    "time_to_first_token_ms": time_to_first_token_ms,
                    "use_case_properties": use_case_properties,
                },
                ingest_units_params.IngestUnitsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IngestResponse,
        )


class IngestResourceWithRawResponse:
    def __init__(self, ingest: IngestResource) -> None:
        self._ingest = ingest

        self.bulk = to_raw_response_wrapper(
            ingest.bulk,
        )
        self.units = to_raw_response_wrapper(
            ingest.units,
        )


class AsyncIngestResourceWithRawResponse:
    def __init__(self, ingest: AsyncIngestResource) -> None:
        self._ingest = ingest

        self.bulk = async_to_raw_response_wrapper(
            ingest.bulk,
        )
        self.units = async_to_raw_response_wrapper(
            ingest.units,
        )


class IngestResourceWithStreamingResponse:
    def __init__(self, ingest: IngestResource) -> None:
        self._ingest = ingest

        self.bulk = to_streamed_response_wrapper(
            ingest.bulk,
        )
        self.units = to_streamed_response_wrapper(
            ingest.units,
        )


class AsyncIngestResourceWithStreamingResponse:
    def __init__(self, ingest: AsyncIngestResource) -> None:
        self._ingest = ingest

        self.bulk = async_to_streamed_response_wrapper(
            ingest.bulk,
        )
        self.units = async_to_streamed_response_wrapper(
            ingest.units,
        )
