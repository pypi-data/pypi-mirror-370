# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ......_models import BaseModel

__all__ = ["EvmTypedData"]


class EvmTypedData(BaseModel):
    domain: object
    """Domain separator for the typed data."""

    message: object
    """Message to be signed.

    Contains the actual data that will be signed with the wallet.
    """

    primary_type: str = FieldInfo(alias="primaryType")
    """Primary type of the typed data."""

    types: object
    """Types used in the typed data."""
