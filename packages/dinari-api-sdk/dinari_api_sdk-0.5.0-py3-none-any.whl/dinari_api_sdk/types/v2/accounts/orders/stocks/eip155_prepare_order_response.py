# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ......_models import BaseModel
from .order_fee_amount import OrderFeeAmount

__all__ = ["Eip155PrepareOrderResponse", "TransactionData"]


class TransactionData(BaseModel):
    abi: object
    """
    [JSON ABI](https://docs.soliditylang.org/en/v0.8.30/abi-spec.html#json) of the
    smart contract function encoded in the transaction. Provided for informational
    purposes.
    """

    args: object
    """Arguments to the smart contract function encoded in the transaction.

    Provided for informational purposes.
    """

    contract_address: str
    """Smart contract address that the transaction should call."""

    data: str
    """Hex-encoded function call."""


class Eip155PrepareOrderResponse(BaseModel):
    fees: List[OrderFeeAmount]
    """Fees included in the order transaction. Provided here as a reference."""

    transaction_data: List[TransactionData]
    """
    List of contract addresses and call data for building transactions to be signed
    and submitted on chain. Transactions should be submitted on chain in the order
    provided in this property.
    """
