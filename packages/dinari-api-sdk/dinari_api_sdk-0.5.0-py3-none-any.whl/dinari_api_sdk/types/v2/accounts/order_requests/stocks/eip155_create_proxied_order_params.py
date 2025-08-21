# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["Eip155CreateProxiedOrderParams"]


class Eip155CreateProxiedOrderParams(TypedDict, total=False):
    order_signature: Required[str]
    """
    Signature of the order typed data, allowing Dinari to place the proxied order on
    behalf of the `Wallet`.
    """

    permit_signature: Required[str]
    """
    Signature of the permit typed data, allowing Dinari to spend the payment token
    or dShare asset token on behalf of the owner.
    """

    prepared_proxied_order_id: Required[str]
    """ID of the prepared proxied order to be submitted as a proxied order."""
