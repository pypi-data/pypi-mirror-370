# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["TemplateRenderDocumentParams"]


class TemplateRenderDocumentParams(TypedDict, total=False):
    slug: Required[str]
    """The slug of the template to use."""

    variables: Required[Dict[str, Union[Iterable[Dict[str, str]], str]]]
    """The variables to use in the template.

    Can be strings or arrays of objects for table data.
    """
