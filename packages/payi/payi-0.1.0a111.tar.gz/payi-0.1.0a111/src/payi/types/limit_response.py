# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .total_cost_data import TotalCostData

__all__ = ["LimitResponse", "Limit"]


class Limit(BaseModel):
    limit_creation_timestamp: datetime

    limit_id: str

    limit_name: str

    limit_type: Literal["block", "allow"]

    limit_update_timestamp: datetime

    max: float

    totals: TotalCostData

    limit_tags: Optional[List[str]] = None

    threshold: Optional[float] = None


class LimitResponse(BaseModel):
    limit: Limit

    request_id: str

    message: Optional[str] = None
