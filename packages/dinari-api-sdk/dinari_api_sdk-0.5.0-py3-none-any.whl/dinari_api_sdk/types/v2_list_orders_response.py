# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from .._models import BaseModel
from .v2.chain import Chain
from .v2.accounts.order_tif import OrderTif
from .v2.accounts.order_side import OrderSide
from .v2.accounts.order_type import OrderType
from .v2.accounts.brokerage_order_status import BrokerageOrderStatus

__all__ = ["V2ListOrdersResponse", "V2ListOrdersResponseItem"]


class V2ListOrdersResponseItem(BaseModel):
    id: str
    """ID of the `Order`."""

    chain_id: Chain
    """
    CAIP-2 formatted chain ID of the blockchain that the `Order` transaction was run
    on.
    """

    created_dt: datetime
    """Datetime at which the `Order` was created. ISO 8601 timestamp."""

    order_contract_address: str
    """Smart contract address that `Order` was created from."""

    order_side: OrderSide
    """Indicates whether `Order` is a buy or sell."""

    order_tif: OrderTif
    """Time in force. Indicates how long `Order` is valid for."""

    order_transaction_hash: str
    """Transaction hash for the `Order` creation."""

    order_type: OrderType
    """Type of `Order`."""

    payment_token: str
    """The payment token (stablecoin) address."""

    status: BrokerageOrderStatus
    """Status of the `Order`."""

    stock_id: str
    """The `Stock` ID associated with the `Order`"""

    account_id: Optional[str] = None
    """Account ID the order was made for."""

    asset_token: Optional[str] = None
    """The dShare asset token address."""

    asset_token_quantity: Optional[float] = None
    """Total amount of assets involved."""

    cancel_transaction_hash: Optional[str] = None
    """Transaction hash for cancellation of `Order`, if the `Order` was cancelled."""

    entity_id: Optional[str] = None
    """Entity ID of the Order"""

    fee: Optional[float] = None
    """Fee amount associated with `Order`."""

    limit_price: Optional[float] = None
    """
    For limit `Orders`, the price per asset, specified in the `Stock`'s native
    currency (USD for US equities and ETFs).
    """

    order_request_id: Optional[str] = None
    """Order Request ID for the `Order`"""

    payment_token_quantity: Optional[float] = None
    """Total amount of payment involved."""


V2ListOrdersResponse: TypeAlias = List[V2ListOrdersResponseItem]
