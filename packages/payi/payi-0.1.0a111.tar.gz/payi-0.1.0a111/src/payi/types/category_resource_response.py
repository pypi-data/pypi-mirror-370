# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["CategoryResourceResponse", "Units"]


class Units(BaseModel):
    input_price: Optional[float] = None

    output_price: Optional[float] = None


class CategoryResourceResponse(BaseModel):
    category: str

    proxy_allowed: bool

    resource: str

    resource_id: str

    start_timestamp: datetime

    units: Dict[str, Units]

    character_billing: Optional[bool] = None

    cost_per_hour: Optional[float] = None

    deprecated_timestamp: Optional[datetime] = None

    large_context_threshold: Optional[int] = None

    max_input_units: Optional[int] = None

    max_output_units: Optional[int] = None

    max_total_units: Optional[int] = None
