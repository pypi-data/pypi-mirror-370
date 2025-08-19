# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FixedCostResourceCreateParams"]


class FixedCostResourceCreateParams(TypedDict, total=False):
    category: Required[str]

    units: Required[List[str]]

    cost_per_hour: float

    start_timestamp: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
