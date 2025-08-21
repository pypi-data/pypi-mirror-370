# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from pydantic import Field as FieldInfo

from .model import Model
from .._models import BaseModel

__all__ = ["ModelList"]


class ModelList(BaseModel):
    data: List[Model]

    http_header: Dict[str, List[str]] = FieldInfo(alias="httpHeader")
