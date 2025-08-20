# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PayerListResponse", "Payer"]


class Payer(BaseModel):
    aliases: List[str]

    display_name: str = FieldInfo(alias="displayName")

    names: List[str]

    primary_payer_id: str = FieldInfo(alias="primaryPayerId")

    stedi_id: str = FieldInfo(alias="stediId")


class PayerListResponse(BaseModel):
    payers: List[Payer]
