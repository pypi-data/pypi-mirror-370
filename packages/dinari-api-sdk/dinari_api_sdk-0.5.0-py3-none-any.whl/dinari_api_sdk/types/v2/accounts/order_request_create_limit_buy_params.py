# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["OrderRequestCreateLimitBuyParams"]


class OrderRequestCreateLimitBuyParams(TypedDict, total=False):
    asset_quantity: Required[float]
    """Amount of dShare asset involved.

    Required for limit `Orders` and market sell `Orders`.
    """

    limit_price: Required[float]
    """Price at which to execute the order.

    Must be a positive number with a precision of up to 2 decimal places.
    """

    stock_id: Required[str]
    """ID of `Stock`."""

    recipient_account_id: str
    """ID of `Account` to receive the `Order`."""
