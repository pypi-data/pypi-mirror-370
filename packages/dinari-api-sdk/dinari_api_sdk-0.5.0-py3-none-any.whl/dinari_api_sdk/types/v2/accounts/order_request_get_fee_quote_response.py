# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["OrderRequestGetFeeQuoteResponse"]


class OrderRequestGetFeeQuoteResponse(BaseModel):
    fee: float
    """Cash amount in USD paid for fees for the Order Request."""
