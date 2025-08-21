# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ......_models import BaseModel

__all__ = ["OrderFeeAmount"]


class OrderFeeAmount(BaseModel):
    fee_in_eth: float
    """
    The quantity of the fee paid via payment token in
    [ETH](https://ethereum.org/en/developers/docs/intro-to-ether/#what-is-ether).
    """

    fee_in_wei: str
    """
    The quantity of the fee paid via payment token in
    [wei](https://ethereum.org/en/developers/docs/intro-to-ether/#denominations).
    """

    type: Literal["SPONSORED_NETWORK", "NETWORK", "TRADING", "ORDER", "PARTNER_ORDER", "PARTNER_TRADING"]
    """Type of fee."""
