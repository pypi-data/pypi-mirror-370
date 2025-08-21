# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["WithdrawalListParams"]


class WithdrawalListParams(TypedDict, total=False):
    page: int

    page_size: int

    withdrawal_request_id: str
    """ID of the `WithdrawalRequest` to find `Withdrawals` for."""
