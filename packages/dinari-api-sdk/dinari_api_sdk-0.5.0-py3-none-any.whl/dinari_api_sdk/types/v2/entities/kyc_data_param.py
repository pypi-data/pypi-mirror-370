# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["KYCDataParam"]


class KYCDataParam(TypedDict, total=False):
    address_country_code: Required[str]
    """Country of residence. ISO 3166-1 alpha 2 country code."""

    country_code: Required[str]
    """Country of citizenship or home country of the organization.

    ISO 3166-1 alpha 2 country code.
    """

    last_name: Required[str]
    """Last name of the person."""

    address_city: str
    """City of address. Not all international addresses use this attribute."""

    address_postal_code: str
    """Postal code of residence address.

    Not all international addresses use this attribute.
    """

    address_street_1: str
    """Street address of address."""

    address_street_2: str
    """Extension of address, usually apartment or suite number."""

    address_subdivision: str
    """State or subdivision of address.

    In the US, this should be the unabbreviated name of the state. Not all
    international addresses use this attribute.
    """

    birth_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """Birth date of the individual. In ISO 8601 format, YYYY-MM-DD."""

    email: str
    """Email address."""

    first_name: str
    """First name of the person."""

    middle_name: str
    """Middle name of the user"""

    tax_id_number: str
    """ID number of the official tax document of the country the entity belongs to."""
