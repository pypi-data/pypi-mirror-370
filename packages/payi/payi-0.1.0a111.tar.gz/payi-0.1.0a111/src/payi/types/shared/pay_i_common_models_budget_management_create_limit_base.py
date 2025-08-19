# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["PayICommonModelsBudgetManagementCreateLimitBase"]


class PayICommonModelsBudgetManagementCreateLimitBase(BaseModel):
    max: float

    limit_tags: Optional[List[str]] = None

    limit_type: Optional[Literal["block", "allow"]] = None

    threshold: Optional[float] = None
