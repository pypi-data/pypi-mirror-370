# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ...._models import BaseModel

__all__ = ["Account"]


class Account(BaseModel):
    id: str
    """Unique ID for the `Account`."""

    created_dt: datetime
    """Datetime when the `Account` was created. ISO 8601 timestamp."""

    entity_id: str
    """ID for the `Entity` that owns the `Account`."""

    is_active: bool
    """Indicates whether the `Account` is active."""
