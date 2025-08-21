# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.openai_usage import OpenAIUsage

__all__ = ["EmbeddingResponse", "Data"]


class Data(BaseModel):
    embedding: List[float]

    index: int

    object: str


class EmbeddingResponse(BaseModel):
    data: List[Data]

    http_header: Dict[str, List[str]] = FieldInfo(alias="httpHeader")

    model: str

    object: str

    usage: OpenAIUsage
