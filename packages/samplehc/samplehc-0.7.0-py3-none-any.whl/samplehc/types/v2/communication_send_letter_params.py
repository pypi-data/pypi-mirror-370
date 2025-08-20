# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "CommunicationSendLetterParams",
    "Document",
    "ToAddress",
    "ToAddressAddress",
    "FromAddress",
    "FromAddressAddress",
]


class CommunicationSendLetterParams(TypedDict, total=False):
    document: Required[Document]
    """The document to send"""

    to_address: Required[Annotated[ToAddress, PropertyInfo(alias="toAddress")]]

    from_address: Annotated[FromAddress, PropertyInfo(alias="fromAddress")]
    """Optional sender address (defaults to Sample Healthcare)"""

    metadata: Dict[str, str]
    """Optional metadata to include with the letter"""

    idempotency_key: Annotated[str, PropertyInfo(alias="Idempotency-Key")]


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]


class ToAddressAddress(TypedDict, total=False):
    city: Required[str]

    state: Required[str]

    street_lines: Required[Annotated[List[str], PropertyInfo(alias="streetLines")]]

    zip_code: Required[Annotated[str, PropertyInfo(alias="zipCode")]]


class ToAddress(TypedDict, total=False):
    address: Required[ToAddressAddress]
    """Recipient's mailing address"""

    name: Required[str]
    """Recipient's name"""


class FromAddressAddress(TypedDict, total=False):
    city: Required[str]

    state: Required[str]

    street_lines: Required[Annotated[List[str], PropertyInfo(alias="streetLines")]]

    zip_code: Required[Annotated[str, PropertyInfo(alias="zipCode")]]


class FromAddress(TypedDict, total=False):
    address: Required[FromAddressAddress]
    """Sender's mailing address"""

    name: Required[str]
    """Sender's name"""
