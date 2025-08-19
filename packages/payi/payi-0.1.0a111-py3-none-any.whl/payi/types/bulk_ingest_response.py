# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.xproxy_error import XproxyError

__all__ = ["BulkIngestResponse", "Error", "ErrorXproxyResult"]


class ErrorXproxyResult(BaseModel):
    message: str

    status_code: int = FieldInfo(alias="statusCode")

    xproxy_error: Optional[XproxyError] = None


class Error(BaseModel):
    item_index: Optional[int] = None

    xproxy_result: Optional[ErrorXproxyResult] = None
    """
    Represents an generic error that occurred as a result of processing a request.
    APIM returns an (not customizable) error response body of { "statusCode",
    "message" } and this class matches this schema. Derived classes may add
    additional required fields if these classes are specified as produced as a
    return type specific endpoints.
    """


class BulkIngestResponse(BaseModel):
    ingest_count: int

    ingest_timestamp: datetime

    request_id: str

    error_count: Optional[int] = None

    errors: Optional[List[Error]] = None

    total_count: Optional[int] = None
