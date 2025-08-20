# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = ["TemplateGenerateDocumentAsyncParams", "Variant0", "Variant1"]


class Variant0(TypedDict, total=False):
    slug: Required[str]
    """The slug of the template to use."""

    type: Required[Literal["document"]]

    document_body: Annotated[object, PropertyInfo(alias="documentBody")]
    """The body of the document."""

    file_name: Annotated[str, PropertyInfo(alias="fileName")]
    """The name of the file to save."""


class Variant1(TypedDict, total=False):
    slug: Required[str]
    """The slug of the template to use."""

    type: Required[Literal["pdf"]]

    variables: Required[Dict[str, Union[str, float, bool, Iterable[Dict[str, Union[str, float]]]]]]
    """The variables to use in the template.

    Arrays will be converted to text representation for PDF form fields.
    """

    file_name: Annotated[str, PropertyInfo(alias="fileName")]
    """The name of the file to save."""


TemplateGenerateDocumentAsyncParams: TypeAlias = Union[Variant0, Variant1]
