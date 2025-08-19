# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["KpiCreateResponse"]


class KpiCreateResponse(BaseModel):
    description: str

    name: str

    request_id: str

    goal: Optional[float] = None

    kpi_type: Optional[Literal["boolean", "number", "percentage", "likert5", "likert7", "likert10"]] = None
