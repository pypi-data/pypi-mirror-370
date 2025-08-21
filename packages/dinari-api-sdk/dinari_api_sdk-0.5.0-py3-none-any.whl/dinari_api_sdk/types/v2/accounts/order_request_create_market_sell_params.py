# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["OrderRequestCreateMarketSellParams"]


class OrderRequestCreateMarketSellParams(TypedDict, total=False):
    asset_quantity: Required[float]
    """Quantity of shares to trade.

    Must be a positive number with a precision of up to 9 decimal places.
    """

    stock_id: Required[str]
    """ID of `Stock`."""

    payment_token_address: str
    """Address of the payment token to be used for the sell order.

    If not provided, the default payment token (USD+) will be used. Should only be
    specified if `recipient_account_id` for a non-managed wallet account is also
    provided.
    """

    recipient_account_id: str
    """ID of `Account` to receive the `Order`."""
