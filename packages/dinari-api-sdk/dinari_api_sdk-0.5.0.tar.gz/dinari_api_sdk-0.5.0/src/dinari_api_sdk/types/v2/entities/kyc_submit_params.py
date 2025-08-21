# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .kyc_data_param import KYCDataParam

__all__ = ["KYCSubmitParams"]


class KYCSubmitParams(TypedDict, total=False):
    data: Required[KYCDataParam]
    """KYC data for an `Entity`."""

    provider_name: Required[str]
    """Name of the KYC provider that provided the KYC information."""
