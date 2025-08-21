# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ....._models import BaseModel

__all__ = ["ExternalGetNonceResponse"]


class ExternalGetNonceResponse(BaseModel):
    message: str
    """Message to be signed by the `Wallet`"""

    nonce: str
    """Single-use identifier"""
