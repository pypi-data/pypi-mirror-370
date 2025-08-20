# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DocumentQueryParams", "Address", "Contact", "PersonalIdentifier"]


class DocumentQueryParams(TypedDict, total=False):
    address: Required[Iterable[Address]]
    """
    An array of Address objects, representing the Patient's current and/or previous
    addresses. May be empty.
    """

    dob: Required[str]
    """The Patient's date of birth (DOB), formatted `YYYY-MM-DD` as per ISO 8601."""

    external_id: Required[Annotated[str, PropertyInfo(alias="externalId")]]
    """An external Patient ID that you store and can use to reference this Patient."""

    first_name: Required[Annotated[str, PropertyInfo(alias="firstName")]]
    """The Patient's first name(s)."""

    gender_at_birth: Required[Annotated[Literal["M", "F", "O", "U"], PropertyInfo(alias="genderAtBirth")]]
    """The Patient's gender at birth, can be one of `M` or `F` or `O` or `U`.

    Use `O` (other) when the patient's gender is known but it is not `M` or `F`, i.e
    intersex or hermaphroditic. Use `U` (unknown) when the patient's gender is not
    known.
    """

    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]
    """The Patient's last name(s)."""

    contact: Iterable[Contact]
    """
    An array of Contact objects, representing the Patient's current and/or previous
    contact information. May be empty.
    """

    personal_identifiers: Annotated[Iterable[PersonalIdentifier], PropertyInfo(alias="personalIdentifiers")]
    """An array of the Patient's personal IDs, such as a driver's license or SSN.

    May be empty.
    """


class Address(TypedDict, total=False):
    address_line1: Required[Annotated[str, PropertyInfo(alias="addressLine1")]]
    """The address."""

    city: Required[str]
    """The city."""

    state: Required[str]
    """The 2 letter state acronym, for example: `CA`."""

    zip: Required[str]
    """5 digit zip code."""

    address_line2: Annotated[str, PropertyInfo(alias="addressLine2")]
    """The address details, for example: `#4451`."""

    country: str
    """If specified, must be `USA`; otherwise will default to `USA`."""


class Contact(TypedDict, total=False):
    email: str
    """The Patient's email address."""

    phone: str
    """The Patient's 10 digit phone number, formatted `1234567899`."""


class PersonalIdentifier(TypedDict, total=False):
    type: Required[Literal["driversLicense", "ssn"]]
    """The ID type - currently `driversLicense` or `ssn` is supported."""

    value: Required[str]
    """The ID number. For type `ssn`, should be 9 digits."""

    state: str
    """The 2 letter state acronym where this ID was issued, for example: `CA`.

    Only required for type `driversLicense`.
    """
