# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ....chain import Chain
from ...order_tif import OrderTif
from ...order_side import OrderSide
from ...order_type import OrderType

__all__ = ["Eip155GetFeeQuoteParams"]


class Eip155GetFeeQuoteParams(TypedDict, total=False):
    chain_id: Required[Chain]
    """CAIP-2 chain ID of the blockchain where the `Order` will be placed."""

    order_side: Required[OrderSide]
    """Indicates whether `Order` is a buy or sell."""

    order_tif: Required[OrderTif]
    """Time in force. Indicates how long `Order` is valid for."""

    order_type: Required[OrderType]
    """Type of `Order`."""

    payment_token: Required[str]
    """Address of payment token."""

    stock_id: Required[str]
    """The ID of the `Stock` for which the `Order` is being placed."""

    asset_token_quantity: float
    """Amount of dShare asset tokens involved.

    Required for limit `Orders` and market sell `Orders`.
    """

    limit_price: float
    """Price per asset in the asset's native currency.

    USD for US equities and ETFs. Required for limit `Orders`.
    """

    payment_token_quantity: float
    """Amount of payment tokens involved. Required for market buy `Orders`."""
