# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CommunicationSendEmailParams", "Attachment"]


class CommunicationSendEmailParams(TypedDict, total=False):
    body: Required[str]
    """The main content/body of the email"""

    subject: Required[str]
    """The subject line of the email"""

    to: Required[str]
    """The email address of the recipient"""

    attach_as_files: Annotated[bool, PropertyInfo(alias="attachAsFiles")]
    """
    When true, files are attached directly to the email instead of as links in the
    body. By default, files are sent as links in the body that require
    authentication with a Sample account, but files attached directly will not
    require authentication. This is useful for recipients without system access.
    """

    attachments: Iterable[Attachment]
    """Optional array of file attachment IDs to include with the email"""

    enable_encryption: Annotated[bool, PropertyInfo(alias="enableEncryption")]
    """Whether to encrypt the email content and send a secure link instead.

    Note that encrypted emails do not support attachments.
    """

    from_: Annotated[str, PropertyInfo(alias="from")]
    """The email address of the sender"""

    zip_attachments: Annotated[bool, PropertyInfo(alias="zipAttachments")]
    """Whether to compress all attachments into a single zip file before sending"""


class Attachment(TypedDict, total=False):
    id: Required[str]
