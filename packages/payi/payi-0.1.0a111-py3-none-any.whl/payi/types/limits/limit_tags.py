# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["LimitTags"]


class LimitTags(BaseModel):
    created_on: Optional[datetime] = None

    tag_id: Optional[int] = None

    tag_name: Optional[str] = None
