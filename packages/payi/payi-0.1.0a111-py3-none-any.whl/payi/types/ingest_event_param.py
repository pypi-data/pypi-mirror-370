# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.ingest_units import IngestUnits
from .pay_i_common_models_api_router_header_info_param import PayICommonModelsAPIRouterHeaderInfoParam

__all__ = ["IngestEventParam", "ProviderResponseFunctionCall"]


class ProviderResponseFunctionCall(TypedDict, total=False):
    name: Required[str]

    arguments: Optional[str]


class IngestEventParam(TypedDict, total=False):
    category: Required[str]

    units: Required[Dict[str, IngestUnits]]

    account_name: Optional[str]

    end_to_end_latency_ms: Optional[int]

    event_timestamp: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    http_status_code: Optional[int]

    limit_ids: Optional[List[str]]

    properties: Optional[Dict[str, str]]

    provider_request_headers: Optional[Iterable[PayICommonModelsAPIRouterHeaderInfoParam]]

    provider_request_json: Optional[str]

    provider_request_reasoning_json: Optional[str]

    provider_response_function_calls: Optional[Iterable[ProviderResponseFunctionCall]]

    provider_response_headers: Optional[Iterable[PayICommonModelsAPIRouterHeaderInfoParam]]

    provider_response_id: Optional[str]

    provider_response_json: Union[str, List[str], None]

    provider_uri: Optional[str]

    request_tags: Optional[List[str]]

    resource: Optional[str]

    time_to_first_completion_token_ms: Optional[int]

    time_to_first_token_ms: Optional[int]

    use_case_id: Optional[str]

    use_case_name: Optional[str]

    use_case_properties: Optional[Dict[str, str]]

    use_case_step: Optional[str]

    use_case_version: Optional[int]

    user_id: Optional[str]
