# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .v2.chain import Chain

__all__ = ["V2ListOrdersParams"]


class V2ListOrdersParams(TypedDict, total=False):
    chain_id: Chain
    """CAIP-2 formatted chain ID of the blockchain the `Order` was made on."""

    order_fulfillment_transaction_hash: str
    """Fulfillment transaction hash of the `Order`."""

    order_request_id: str
    """Order Request ID for the `Order`"""

    order_transaction_hash: str
    """Transaction hash of the `Order`."""

    page: int

    page_size: int
