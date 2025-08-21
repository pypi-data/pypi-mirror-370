# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from ......_models import BaseModel
from .evm_typed_data import EvmTypedData
from ...orders.stocks.order_fee_amount import OrderFeeAmount

__all__ = ["Eip155PrepareProxiedOrderResponse"]


class Eip155PrepareProxiedOrderResponse(BaseModel):
    id: str
    """ID of the EvmPreparedProxiedOrder."""

    deadline: datetime
    """Deadline for the prepared order to be placed."""

    fees: List[OrderFeeAmount]
    """Fees involved in the order. Provided here as a reference."""

    order_typed_data: EvmTypedData
    """
    [EIP-712](https://eips.ethereum.org/EIPS/eip-712) typed data to be signed with a
    wallet.
    """

    permit_typed_data: EvmTypedData
    """
    [EIP-712](https://eips.ethereum.org/EIPS/eip-712) typed data to be signed with a
    wallet.
    """
