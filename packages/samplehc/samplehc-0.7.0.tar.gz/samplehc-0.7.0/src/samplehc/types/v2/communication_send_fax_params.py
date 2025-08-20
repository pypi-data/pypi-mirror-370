# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CommunicationSendFaxParams", "Document"]


class CommunicationSendFaxParams(TypedDict, total=False):
    document: Required[Document]
    """The document to be sent via fax"""

    to: Required[str]
    """The fax number to send the document to"""

    batch_delay_seconds: Annotated[str, PropertyInfo(alias="batchDelaySeconds")]
    """
    The delay between each batch of faxes in seconds, only used if enableBatchDelay
    is true, defaults to 60 seconds
    """

    enable_batch_collision_avoidance: Annotated[bool, PropertyInfo(alias="enableBatchCollisionAvoidance")]
    """
    Recommended for high-volume fax operations or when sending to recipients who may
    receive multiple faxes simultaneously. Prevents transmission failures by
    automatically queuing your fax when another transmission to the same number is
    already in progress. Your fax will wait and automatically send once the line is
    clear, ensuring reliable delivery without manual intervention.
    """

    enable_batch_delay: Annotated[bool, PropertyInfo(alias="enableBatchDelay")]
    """
    If enabled, the fax will be sent in batches according to the specified batch
    delay timing.
    """


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
