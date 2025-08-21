# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ....chain import Chain
from ......_models import BaseModel
from .order_fee_amount import OrderFeeAmount

__all__ = ["Eip155GetFeeQuoteResponse", "OrderFeeContractObject", "OrderFeeContractObjectFeeQuote"]


class OrderFeeContractObjectFeeQuote(BaseModel):
    deadline: int

    fee: str

    order_id: str = FieldInfo(alias="orderId")

    requester: str

    timestamp: int


class OrderFeeContractObject(BaseModel):
    chain_id: Literal[42161, 1, 8453, 81457, 7887, 98866]
    """EVM chain ID of the blockchain where the `Order` will be placed."""

    fee_quote: OrderFeeContractObjectFeeQuote
    """`FeeQuote` structure to pass into contracts."""

    fee_quote_signature: str
    """Signed `FeeQuote` structure to pass into contracts."""

    fees: List[OrderFeeAmount]
    """Breakdown of fees"""

    payment_token: str
    """Address of payment token used for fees"""


class Eip155GetFeeQuoteResponse(BaseModel):
    chain_id: Chain
    """CAIP-2 chain ID of the blockchain where the `Order` will be placed"""

    fee: float
    """The total quantity of the fees paid via payment token."""

    order_fee_contract_object: OrderFeeContractObject
    """
    Opaque fee quote object to pass into the contract when creating an `Order`
    directly through Dinari's smart contracts.
    """
