# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

__all__ = ["StockListParams"]


class StockListParams(TypedDict, total=False):
    page: int

    page_size: int

    symbols: List[str]
    """List of `Stock` symbols to query. If not provided, all `Stocks` are returned."""
