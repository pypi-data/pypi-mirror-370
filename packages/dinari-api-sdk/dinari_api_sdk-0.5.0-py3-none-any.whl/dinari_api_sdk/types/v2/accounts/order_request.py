# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .order_tif import OrderTif
from ...._models import BaseModel
from .order_side import OrderSide
from .order_type import OrderType

__all__ = ["OrderRequest"]


class OrderRequest(BaseModel):
    id: str
    """ID of `OrderRequest`.

    This is the primary identifier for the `/order_requests` routes.
    """

    account_id: str
    """ID of `Account` placing the `OrderRequest`."""

    created_dt: datetime
    """Datetime at which the `OrderRequest` was created. ISO 8601 timestamp."""

    order_side: OrderSide
    """Indicates whether `Order` is a buy or sell."""

    order_tif: OrderTif
    """Indicates how long `Order` is valid for."""

    order_type: OrderType
    """Type of `Order`."""

    status: Literal["PENDING", "SUBMITTED", "ERROR", "CANCELLED"]
    """Status of `OrderRequest`."""

    order_id: Optional[str] = None
    """ID of `Order` created from the `OrderRequest`.

    This is the primary identifier for the `/orders` routes.
    """

    recipient_account_id: Optional[str] = None
    """ID of recipient `Account`."""
