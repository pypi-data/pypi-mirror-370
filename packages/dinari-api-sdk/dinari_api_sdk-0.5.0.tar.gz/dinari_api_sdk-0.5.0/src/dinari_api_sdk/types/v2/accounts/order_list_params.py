# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..chain import Chain

__all__ = ["OrderListParams"]


class OrderListParams(TypedDict, total=False):
    chain_id: Chain
    """CAIP-2 formatted chain ID of the blockchain the `Order` was made on."""

    order_transaction_hash: str
    """Transaction hash of the `Order`."""

    page: int

    page_size: int
