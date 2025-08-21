# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .chain import Chain
from ..._models import BaseModel

__all__ = ["AccountGetPortfolioResponse", "Asset"]


class Asset(BaseModel):
    amount: float
    """Total amount of the dShare asset token in the `Account`."""

    chain_id: Chain
    """CAIP-2 chain ID of the blockchain where the dShare asset token exists."""

    stock_id: str
    """ID of the underlying `Stock` represented by the dShare asset token."""

    symbol: str
    """Token symbol of the dShare asset token."""

    token_address: str
    """Address of the dShare asset token."""


class AccountGetPortfolioResponse(BaseModel):
    assets: List[Asset]
    """Balance details for all owned `Stocks`."""
