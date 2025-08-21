# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Model", "Permission"]


class Permission(BaseModel):
    id: str

    allow_create_engine: bool

    allow_fine_tuning: bool

    allow_logprobs: bool

    allow_sampling: bool

    allow_search_indices: bool

    allow_view: bool

    created: int

    group: object

    is_blocking: bool

    object: str

    organization: str


class Model(BaseModel):
    id: str

    created: int

    http_header: Dict[str, List[str]] = FieldInfo(alias="httpHeader")

    object: str

    owned_by: str

    parent: str

    permission: List[Permission]

    root: str
