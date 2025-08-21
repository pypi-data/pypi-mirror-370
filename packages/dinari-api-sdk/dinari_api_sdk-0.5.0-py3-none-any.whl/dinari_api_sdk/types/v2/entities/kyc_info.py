# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .kyc_data import KYCData
from ...._models import BaseModel

__all__ = ["KYCInfo"]


class KYCInfo(BaseModel):
    id: str
    """ID of the KYC check."""

    status: Literal["PASS", "FAIL", "PENDING", "INCOMPLETE"]
    """KYC check status."""

    checked_dt: Optional[datetime] = None
    """Datetime when the KYC was last checked. ISO 8601 timestamp."""

    data: Optional[KYCData] = None
    """KYC data for an `Entity`."""
